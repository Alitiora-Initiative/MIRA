package main

import (
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

// Pending transaction
type PendingTransaction struct {
	Hash           string  `json:"hash"`
	From           string  `json:"from"`
	To             string  `json:"to"`
	Value          float64 `json:"value"`
	GasPrice       float64 `json:"gas_price"`
	GasLimit       uint64  `json:"gas_limit"`
	Nonce          uint64  `json:"nonce"`
	Timestamp      int64   `json:"timestamp"`
	PoolAddress    string  `json:"pool_address,omitempty"`
}

// Flash loan opportunity
type FlashLoanOpportunity struct {
	PoolAddress   string  `json:"pool_address"`
	TokenA        string  `json:"token_a"`
	TokenB        string  `json:"token_b"`
	Profit        float64 `json:"profit"`
	EstimatedGas  float64 `json:"estimated_gas"`
	Timestamp     int64   `json:"timestamp"`
}

// MempoolMonitor monitors pending transactions
type MempoolMonitor struct {
	rpcEndpoints      []string
	kafkaBrokers      []string
	kafkaProducer    sarama.SyncProducer
	wsConnections     map[string]*websocket.Conn
	wsMutex           sync.RWMutex
	pendingTxs        map[string]PendingTransaction
	txMutex           sync.RWMutex
	logger            *logrus.Logger
	reconnectDelay    time.Duration
	maxReconnectDelay time.Duration
}

func NewMempoolMonitor(rpcEndpoints []string, kafkaBrokers []string) *MempoolMonitor {
	logger := logrus.New()
	logger.SetFormatter(&logrus.JSONFormatter{})
	logger.SetLevel(logrus.InfoLevel)

	return &MempoolMonitor{
		rpcEndpoints:      rpcEndpoints,
		kafkaBrokers:      kafkaBrokers,
		wsConnections:     make(map[string]*websocket.Conn),
		pendingTxs:        make(map[string]PendingTransaction),
		reconnectDelay:    1 * time.Second,
		maxReconnectDelay: 30 * time.Second,
		logger:            logger,
	}
}

func (mm *MempoolMonitor) connectKafka() error {
	config := sarama.NewConfig()
	config.Producer.RequiredAcks = sarama.WaitForAll
	config.Producer.Retry.Max = 5
	config.Producer.Return.Successes = true

	producer, err := sarama.NewSyncProducer(mm.kafkaBrokers, config)
	if err != nil {
		return fmt.Errorf("failed to create Kafka producer: %w", err)
	}

	mm.kafkaProducer = producer
	mm.logger.Info("Connected to Kafka")
	return nil
}

func (mm *MempoolMonitor) connectWebSocket(endpoint string) error {
	mm.logger.Infof("Connecting to mempool WebSocket: %s", endpoint)

	ws, _, err := websocket.DefaultDialer.Dial(endpoint, nil)
	if err != nil {
		return fmt.Errorf("WebSocket dial error: %w", err)
	}

	mm.wsMutex.Lock()
	mm.wsConnections[endpoint] = ws
	mm.wsMutex.Unlock()

	// Subscribe to pending transactions
	subscribeMsg := map[string]interface{}{
		"jsonrpc": "2.0",
		"id":      1,
		"method":  "signatureSubscribe",
		"params": []interface{}{
			"11111111111111111111111111111111",
		},
	}

	if err := ws.WriteJSON(subscribeMsg); err != nil {
		return fmt.Errorf("failed to send subscription: %w", err)
	}

	mm.logger.Infof("Successfully connected to mempool WebSocket: %s", endpoint)
	return nil
}

func (mm *MempoolMonitor) detectFrontRunning(newTx PendingTransaction) bool {
	mm.txMutex.RLock()
	defer mm.txMutex.RUnlock()

	// Check for similar pending transactions
	for _, pendingTx := range mm.pendingTxs {
		// Same pool and opposite direction could indicate front-running
		if pendingTx.PoolAddress == newTx.PoolAddress &&
			pendingTx.To == newTx.From &&
			time.Since(time.Unix(pendingTx.Timestamp, 0)) < 5*time.Second {
			mm.logger.Warnf("Potential front-running detected: %s", newTx.Hash)
			return true
		}
	}

	return false
}

func (mm *MempoolMonitor) detectFlashLoan(tx PendingTransaction) *FlashLoanOpportunity {
	// Simplified flash loan detection
	// In production, this would analyze arbitrage opportunities

	if tx.Value > 10000 && tx.GasPrice < 50 {
		return &FlashLoanOpportunity{
			PoolAddress:  tx.PoolAddress,
			TokenA:       "SOL",
			TokenB:       "USDC",
			Profit:       tx.Value * 0.01, // 1% profit estimate
			EstimatedGas: tx.GasLimit * tx.GasPrice,
			Timestamp:    time.Now().Unix(),
		}
	}

	return nil
}

func (mm *MempoolMonitor) processPendingTransaction(tx PendingTransaction) {
	// Check for front-running
	if mm.detectFrontRunning(tx) {
		// Publish alert
		mm.publishToKafka("mempool.front_run_alert", tx)
	}

	// Check for flash loan opportunities
	if flashLoan := mm.detectFlashLoan(tx); flashLoan != nil {
		mm.publishToKafka("mempool.flash_loans", flashLoan)
	}

	// Store pending transaction
	mm.txMutex.Lock()
	mm.pendingTxs[tx.Hash] = tx
	mm.txMutex.Unlock()

	// Publish to Kafka
	mm.publishToKafka("mempool.solana.pending", tx)
}

func (mm *MempoolMonitor) publishToKafka(topic string, event interface{}) error {
	data, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}

	msg := &sarama.ProducerMessage{
		Topic: topic,
		Value: sarama.ByteEncoder(data),
	}

	_, _, err = mm.kafkaProducer.SendMessage(msg)
	if err != nil {
		return fmt.Errorf("failed to send message: %w", err)
	}

	mm.logger.WithField("topic", topic).Info("Message published to Kafka")
	return nil
}

func (mm *MempoolMonitor) cleanupOldTransactions() {
	ticker := time.NewTicker(1 * time.Minute)
	defer ticker.Stop()

	for range ticker.C {
		mm.txMutex.Lock()
		for hash, tx := range mm.pendingTxs {
			if time.Since(time.Unix(tx.Timestamp, 0)) > 5*time.Minute {
				delete(mm.pendingTxs, hash)
			}
		}
		mm.txMutex.Unlock()
	}
}

func (mm *MempoolMonitor) listenWebSocket(endpoint string) {
	for {
		mm.wsMutex.RLock()
		ws, exists := mm.wsConnections[endpoint]
		mm.wsMutex.RUnlock()

		if !exists {
			mm.logger.Warnf("WebSocket connection not found for %s", endpoint)
			time.Sleep(mm.reconnectDelay)
			continue
		}

		var message map[string]interface{}
		if err := ws.ReadJSON(&message); err != nil {
			mm.logger.Errorf("WebSocket read error: %v", err)
			mm.handleDisconnect(endpoint)
			continue
		}

		// Simulate pending transaction
		pendingTx := PendingTransaction{
			Hash:        fmt.Sprintf("0x%x", time.Now().UnixNano()),
			From:        "from_address",
			To:          "to_address",
			Value:       1000.0,
			GasPrice:    25.0,
			GasLimit:    100000,
			Nonce:       uint64(time.Now().Unix()),
			Timestamp:   time.Now().Unix(),
			PoolAddress: "pool_address",
		}

		mm.processPendingTransaction(pendingTx)
	}
}

func (mm *MempoolMonitor) handleDisconnect(endpoint string) {
	mm.wsMutex.Lock()
	if ws, exists := mm.wsConnections[endpoint]; exists {
		ws.Close()
		delete(mm.wsConnections, endpoint)
	}
	mm.wsMutex.Unlock()
}

func (mm *MempoolMonitor) Start() error {
	if err := mm.connectKafka(); err != nil {
		return err
	}
	defer mm.kafkaProducer.Close()

	// Start cleanup goroutine
	go mm.cleanupOldTransactions()

	// Connect to WebSocket endpoints
	var wg sync.WaitGroup
	for _, endpoint := range mm.rpcEndpoints {
		wg.Add(1)
		go func(ep string) {
			defer wg.Done()
			if err := mm.connectWebSocket(ep); err != nil {
				mm.logger.Errorf("Failed to connect to %s: %v", ep, err)
				return
			}
			mm.listenWebSocket(ep)
		}(endpoint)
	}

	// Wait for interrupt signal
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	<-sigChan

	mm.logger.Info("Shutting down...")
	wg.Wait()

	return nil
}

func main() {
	rpcEndpoints := []string{
		"wss://api.devnet.solana.com",
	}

	kafkaBrokers := []string{
		"localhost:9092",
	}

	monitor := NewMempoolMonitor(rpcEndpoints, kafkaBrokers)

	if err := monitor.Start(); err != nil {
		log.Fatalf("Mempool monitor failed: %v", err)
	}
}
