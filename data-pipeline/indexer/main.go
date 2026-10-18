package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	"github.com/Shopify/sarama"
	"github.com/gorilla/websocket"
	"github.com/sirupsen/logrus"
)

// Solana WebSocket message structure
type SolanaWSMessage struct {
	Jsonrpc string `json:"jsonrpc"`
	Method  string `json:"method"`
	Params  struct {
		Result struct {
			Subscription int64  `json:"subscription"`
			Result       string `json:"result"`
		} `json:"result"`
	} `json:"params"`
}

// Transfer event
type TransferEvent struct {
	Signature   string  `json:"signature"`
	From        string  `json:"from"`
	To          string  `json:"to"`
	Amount      float64 `json:"amount"`
	Token       string  `json:"token"`
	Timestamp   int64   `json:"timestamp"`
	BlockNumber int64   `json:"block_number"`
}

// Swap event
type SwapEvent struct {
	Signature    string  `json:"signature"`
	PoolAddress  string  `json:"pool_address"`
	TokenIn      string  `json:"token_in"`
	TokenOut     string  `json:"token_out"`
	AmountIn     float64 `json:"amount_in"`
	AmountOut    float64 `json:"amount_out"`
	PriceImpact  float64 `json:"price_impact"`
	Timestamp    int64   `json:"timestamp"`
	BlockNumber  int64   `json:"block_number"`
}

// BlockchainIndexer manages WebSocket connections to RPC nodes
type BlockchainIndexer struct {
	rpcEndpoints      []string
	kafkaBrokers      []string
	kafkaProducer    sarama.SyncProducer
	wsConnections     map[string]*websocket.Conn
	wsMutex           sync.RWMutex
	reconnectDelay    time.Duration
	maxReconnectDelay time.Duration
	logger            *logrus.Logger
	ctx               context.Context
	cancel            context.CancelFunc
}

func NewBlockchainIndexer(rpcEndpoints []string, kafkaBrokers []string) *BlockchainIndexer {
	ctx, cancel := context.WithCancel(context.Background())

	logger := logrus.New()
	logger.SetFormatter(&logrus.JSONFormatter{})
	logger.SetLevel(logrus.InfoLevel)

	return &BlockchainIndexer{
		rpcEndpoints:      rpcEndpoints,
		kafkaBrokers:      kafkaBrokers,
		wsConnections:     make(map[string]*websocket.Conn),
		reconnectDelay:    1 * time.Second,
		maxReconnectDelay: 30 * time.Second,
		logger:            logger,
		ctx:               ctx,
		cancel:            cancel,
	}
}

func (bi *BlockchainIndexer) connectKafka() error {
	config := sarama.NewConfig()
	config.Producer.RequiredAcks = sarama.WaitForAll
	config.Producer.Retry.Max = 5
	config.Producer.Return.Successes = true

	producer, err := sarama.NewSyncProducer(bi.kafkaBrokers, config)
	if err != nil {
		return fmt.Errorf("failed to create Kafka producer: %w", err)
	}

	bi.kafkaProducer = producer
	bi.logger.Info("Connected to Kafka")
	return nil
}

func (bi *BlockchainIndexer) connectWebSocket(endpoint string) error {
	bi.logger.Infof("Connecting to WebSocket: %s", endpoint)

	ws, _, err := websocket.DefaultDialer.Dial(endpoint, nil)
	if err != nil {
		return fmt.Errorf("WebSocket dial error: %w", err)
	}

	bi.wsMutex.Lock()
	bi.wsConnections[endpoint] = ws
	bi.wsMutex.Unlock()

	// Subscribe to account notifications
	subscribeMsg := map[string]interface{}{
		"jsonrpc": "2.0",
		"id":      1,
		"method":  "accountSubscribe",
		"params": []interface{}{
			"11111111111111111111111111111111", // System program
			{
				"encoding":   "jsonParsed",
				"commitment": "confirmed",
			},
		},
	}

	if err := ws.WriteJSON(subscribeMsg); err != nil {
		return fmt.Errorf("failed to send subscription: %w", err)
	}

	bi.logger.Infof("Successfully connected to WebSocket: %s", endpoint)
	return nil
}

func (bi *BlockchainIndexer) listenWebSocket(endpoint string) {
	defer bi.cancel()

	for {
		select {
		case <-bi.ctx.Done():
			return
		default:
			bi.wsMutex.RLock()
			ws, exists := bi.wsConnections[endpoint]
			bi.wsMutex.RUnlock()

			if !exists {
				bi.logger.Warnf("WebSocket connection not found for %s, reconnecting...", endpoint)
				if err := bi.reconnectWebSocket(endpoint); err != nil {
					bi.logger.Errorf("Reconnect failed: %v", err)
					time.Sleep(bi.reconnectDelay)
					continue
				}
				ws = bi.wsConnections[endpoint]
			}

			var message SolanaWSMessage
			if err := ws.ReadJSON(&message); err != nil {
				bi.logger.Errorf("WebSocket read error: %v", err)
				bi.handleDisconnect(endpoint)
				continue
			}

			// Process message
			bi.processMessage(message)
		}
	}
}

func (bi *BlockchainIndexer) processMessage(message SolanaWSMessage) {
	// In production, parse actual Solana transactions
	// For now, we'll simulate events

	// Simulate transfer event
	transfer := TransferEvent{
		Signature:   fmt.Sprintf("sig_%d", time.Now().UnixNano()),
		From:        "from_address",
		To:          "to_address",
		Amount:      100.0,
		Token:       "SOL",
		Timestamp:   time.Now().Unix(),
		BlockNumber: time.Now().Unix(),
	}

	bi.publishToKafka("blockchain.solana.transfers", transfer)

	// Simulate swap event
	swap := SwapEvent{
		Signature:   fmt.Sprintf("swap_%d", time.Now().UnixNano()),
		PoolAddress: "pool_address",
		TokenIn:     "SOL",
		TokenOut:    "USDC",
		AmountIn:    100.0,
		AmountOut:   99.5,
		PriceImpact: 0.5,
		Timestamp:   time.Now().Unix(),
		BlockNumber: time.Now().Unix(),
	}

	bi.publishToKafka("blockchain.solana.swaps", swap)
}

func (bi *BlockchainIndexer) publishToKafka(topic string, event interface{}) error {
	data, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}

	msg := &sarama.ProducerMessage{
		Topic: topic,
		Value: sarama.ByteEncoder(data),
	}

	partition, offset, err := bi.kafkaProducer.SendMessage(msg)
	if err != nil {
		return fmt.Errorf("failed to send message: %w", err)
	}

	bi.logger.WithFields(logrus.Fields{
		"topic":     topic,
		"partition": partition,
		"offset":    offset,
	}).Info("Message published to Kafka")

	return nil
}

func (bi *BlockchainIndexer) handleDisconnect(endpoint string) {
	bi.wsMutex.Lock()
	if ws, exists := bi.wsConnections[endpoint]; exists {
		ws.Close()
		delete(bi.wsConnections, endpoint)
	}
	bi.wsMutex.Unlock()
}

func (bi *BlockchainIndexer) reconnectWebSocket(endpoint string) error {
	bi.logger.Infof("Reconnecting to WebSocket: %s", endpoint)

	delay := bi.reconnectDelay
	for {
		select {
		case <-bi.ctx.Done():
			return bi.ctx.Err()
		default:
			if err := bi.connectWebSocket(endpoint); err == nil {
				bi.reconnectDelay = 1 * time.Second // Reset delay
				return nil
			}

			bi.logger.Errorf("Reconnect attempt failed: %v, retrying in %v", err, delay)
			time.Sleep(delay)

			delay = time.Duration(float64(delay) * 1.5)
			if delay > bi.maxReconnectDelay {
				delay = bi.maxReconnectDelay
			}
		}
	}
}

func (bi *BlockchainIndexer) Start() error {
	// Connect to Kafka
	if err := bi.connectKafka(); err != nil {
		return err
	}
	defer bi.kafkaProducer.Close()

	// Connect to all WebSocket endpoints
	var wg sync.WaitGroup
	for _, endpoint := range bi.rpcEndpoints {
		wg.Add(1)
		go func(ep string) {
			defer wg.Done()
			if err := bi.connectWebSocket(ep); err != nil {
				bi.logger.Errorf("Failed to connect to %s: %v", ep, err)
				return
			}
			bi.listenWebSocket(ep)
		}(endpoint)
	}

	// Wait for interrupt signal
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	<-sigChan

	bi.logger.Info("Shutting down...")
	bi.cancel()
	wg.Wait()

	return nil
}

func main() {
	rpcEndpoints := []string{
		"wss://api.devnet.solana.com",
		"wss://solana-api.projectserum.com",
	}

	kafkaBrokers := []string{
		"localhost:9092",
	}

	indexer := NewBlockchainIndexer(rpcEndpoints, kafkaBrokers)

	if err := indexer.Start(); err != nil {
		log.Fatalf("Indexer failed: %v", err)
	}
}
