package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/Shopify/sarama"
	"github.com/sirupsen/logrus"
)

// Normalized data structure
type NormalizedEvent struct {
	Chain       string                 `json:"chain"`
	EventType   string                 `json:"event_type"`   // transfer, swap, liquidity
	Timestamp   int64                  `json:"timestamp"`
	Signature   string                 `json:"signature"`
	From        string                 `json:"from"`
	To          string                 `json:"to"`
	Amount      float64                `json:"amount"`
	Token       string                 `json:"token"`
	PoolAddress string                 `json:"pool_address,omitempty"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
}

// DataNormalizer normalizes data from multiple chains
type DataNormalizer struct {
	kafkaBrokers   []string
	kafkaConsumer  sarama.ConsumerGroup
	kafkaProducer  sarama.SyncProducer
	inputTopics    []string
	outputTopic    string
	logger         *logrus.Logger
}

func NewDataNormalizer(kafkaBrokers []string, inputTopics []string, outputTopic string) *DataNormalizer {
	logger := logrus.New()
	logger.SetFormatter(&logrus.JSONFormatter{})
	logger.SetLevel(logrus.InfoLevel)

	return &DataNormalizer{
		kafkaBrokers: kafkaBrokers,
		inputTopics:  inputTopics,
		outputTopic:  outputTopic,
		logger:       logger,
	}
}

func (dn *DataNormalizer) connectKafka() error {
	// Producer config
	producerConfig := sarama.NewConfig()
	producerConfig.Producer.RequiredAcks = sarama.WaitForAll
	producerConfig.Producer.Return.Successes = true

	producer, err := sarama.NewSyncProducer(dn.kafkaBrokers, producerConfig)
	if err != nil {
		return fmt.Errorf("failed to create Kafka producer: %w", err)
	}
	dn.kafkaProducer = producer

	// Consumer config
	consumerConfig := sarama.NewConfig()
	consumerConfig.Consumer.Group.Rebalance.Strategy = sarama.BalanceStrategyRoundRobin
	consumerConfig.Consumer.Offsets.Initial = sarama.OffsetNewest

	consumerGroup, err := sarama.NewConsumerGroup(dn.kafkaBrokers, "normalizer-group", consumerConfig)
	if err != nil {
		return fmt.Errorf("failed to create consumer group: %w", err)
	}
	dn.kafkaConsumer = consumerGroup

	dn.logger.Info("Connected to Kafka")
	return nil
}

func asString(data map[string]interface{}, key string) (string, error) {
	value, ok := data[key]
	if !ok || value == nil {
		return "", fmt.Errorf("missing %s", key)
	}
	text, ok := value.(string)
	if !ok || text == "" {
		return "", fmt.Errorf("%s is not a string", key)
	}
	return text, nil
}

func asFloat(data map[string]interface{}, key string) (float64, error) {
	value, ok := data[key]
	if !ok || value == nil {
		return 0, fmt.Errorf("missing %s", key)
	}
	switch number := value.(type) {
	case float64:
		return number, nil
	case json.Number:
		return number.Float64()
	default:
		return 0, fmt.Errorf("%s is not a number", key)
	}
}

func (dn *DataNormalizer) normalizeTransfer(data map[string]interface{}) (NormalizedEvent, error) {
	timestamp, err := asFloat(data, "timestamp")
	if err != nil {
		return NormalizedEvent{}, err
	}
	signature, err := asString(data, "signature")
	if err != nil {
		return NormalizedEvent{}, err
	}
	from, err := asString(data, "from")
	if err != nil {
		return NormalizedEvent{}, err
	}
	to, err := asString(data, "to")
	if err != nil {
		return NormalizedEvent{}, err
	}
	amount, err := asFloat(data, "amount")
	if err != nil {
		return NormalizedEvent{}, err
	}
	token, err := asString(data, "token")
	if err != nil {
		return NormalizedEvent{}, err
	}
	return NormalizedEvent{
		Chain:     "solana",
		EventType: "transfer",
		Timestamp: int64(timestamp),
		Signature: signature,
		From:      from,
		To:        to,
		Amount:    amount,
		Token:     token,
		Metadata:  make(map[string]interface{}),
	}, nil
}

func (dn *DataNormalizer) normalizeSwap(data map[string]interface{}) (NormalizedEvent, error) {
	timestamp, err := asFloat(data, "timestamp")
	if err != nil {
		return NormalizedEvent{}, err
	}
	signature, err := asString(data, "signature")
	if err != nil {
		return NormalizedEvent{}, err
	}
	pool, err := asString(data, "pool_address")
	if err != nil {
		return NormalizedEvent{}, err
	}
	amount, err := asFloat(data, "amount_in")
	if err != nil {
		return NormalizedEvent{}, err
	}
	token, err := asString(data, "token_in")
	if err != nil {
		return NormalizedEvent{}, err
	}
	return NormalizedEvent{
		Chain:       "solana",
		EventType:   "swap",
		Timestamp:   int64(timestamp),
		Signature:   signature,
		From:        pool,
		To:          pool,
		Amount:      amount,
		Token:       token,
		PoolAddress: pool,
		Metadata: map[string]interface{}{
			"token_out":    data["token_out"],
			"amount_out":   data["amount_out"],
			"price_impact": data["price_impact"],
			"block_number": data["block_number"],
		},
	}, nil
}

func (dn *DataNormalizer) processMessage(data []byte) error {
	var rawMsg map[string]interface{}
	if err := json.Unmarshal(data, &rawMsg); err != nil {
		return fmt.Errorf("failed to unmarshal message: %w", err)
	}

	var normalized NormalizedEvent
	var err error

	if _, ok := rawMsg["token_in"].(string); ok {
		normalized, err = dn.normalizeSwap(rawMsg)
	} else {
		normalized, err = dn.normalizeTransfer(rawMsg)
	}
	if err != nil {
		return fmt.Errorf("drop malformed event: %w", err)
	}

	// Publish normalized event
	return dn.publishNormalized(normalized)
}

func (dn *DataNormalizer) publishNormalized(event NormalizedEvent) error {
	data, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal normalized event: %w", err)
	}

	msg := &sarama.ProducerMessage{
		Topic: dn.outputTopic,
		Value: sarama.ByteEncoder(data),
	}

	_, _, err = dn.kafkaProducer.SendMessage(msg)
	if err != nil {
		return fmt.Errorf("failed to send normalized message: %w", err)
	}

	dn.logger.WithFields(logrus.Fields{
		"chain":      event.Chain,
		"event_type": event.EventType,
		"signature":  event.Signature,
	}).Info("Normalized event published")

	return nil
}

func (dn *DataNormalizer) Start() error {
	if err := dn.connectKafka(); err != nil {
		return err
	}
	defer dn.kafkaConsumer.Close()
	defer dn.kafkaProducer.Close()

	// Create consumer group handler
	handler := &NormalizerHandler{normalizer: dn}

	// Start consuming
	ctx := context.Background()
	for {
		if err := dn.kafkaConsumer.Consume(ctx, dn.inputTopics, handler); err != nil {
			dn.logger.Errorf("Error from consumer: %v", err)
		}

		// Check if context was cancelled
		if ctx.Err() != nil {
			break
		}
	}

	return nil
}

// NormalizerHandler implements sarama.ConsumerGroupHandler
type NormalizerHandler struct {
	normalizer *DataNormalizer
}

func (h *NormalizerHandler) Setup(sarama.ConsumerGroupSession) error   { return nil }
func (h *NormalizerHandler) Cleanup(sarama.ConsumerGroupSession) error { return nil }

func (h *NormalizerHandler) ConsumeClaim(session sarama.ConsumerGroupSession, claim sarama.ConsumerGroupClaim) error {
	for message := range claim.Messages() {
		if err := h.normalizer.processMessage(message.Value); err != nil {
			h.normalizer.logger.Errorf("Failed to process message: %v", err)
		}
		session.MarkMessage(message, "")
	}
	return nil
}

func main() {
	kafkaBrokers := []string{"localhost:9092"}
	inputTopics := []string{
		"blockchain.solana.transfers",
		"blockchain.solana.swaps",
	}
	outputTopic := "blockchain.normalized"

	normalizer := NewDataNormalizer(kafkaBrokers, inputTopics, outputTopic)

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		if err := normalizer.Start(); err != nil {
			log.Fatalf("Normalizer failed: %v", err)
		}
	}()

	<-sigChan
	log.Println("Shutting down...")
}
