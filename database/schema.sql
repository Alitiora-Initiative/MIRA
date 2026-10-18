-- MIRA Trading Agent Database Schema
-- PostgreSQL schema for multi-asset trading

-- Asset Registry
CREATE TABLE IF NOT EXISTS asset_registry (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    asset_type VARCHAR(20) NOT NULL,  -- 'memecoin', 'tokenized_stock', 'perp'
    chain VARCHAR(20),  -- 'solana', 'ethereum', 'ceex'
    contract_address VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, chain)
);

-- On-chain Transactions
CREATE TABLE IF NOT EXISTS on_chain_transactions (
    id SERIAL PRIMARY KEY,
    tx_hash VARCHAR(100) UNIQUE NOT NULL,
    chain VARCHAR(20) NOT NULL,
    from_address VARCHAR(100),
    to_address VARCHAR(100),
    value_usd DECIMAL(20, 8),
    gas_used BIGINT,
    block_number BIGINT,
    timestamp TIMESTAMP,
    tx_type VARCHAR(50)  -- 'swap', 'transfer', 'approval', etc.
);

-- Wallet Balances
CREATE TABLE IF NOT EXISTS wallet_balances (
    id SERIAL PRIMARY KEY,
    wallet_address VARCHAR(100) NOT NULL,
    asset_symbol VARCHAR(50) NOT NULL,
    balance DECIMAL(30, 18),
    balance_usd DECIMAL(20, 8),
    timestamp TIMESTAMP DEFAULT NOW(),
    UNIQUE(wallet_address, asset_symbol, timestamp)
);

-- Performance Metrics
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    metric_type VARCHAR(50) NOT NULL,  -- 'daily_pnl', 'sharpe', 'max_drawdown'
    asset_class VARCHAR(20),
    value DECIMAL(20, 8),
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Webhook Signals
CREATE TABLE IF NOT EXISTS webhook_signals (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,  -- 'tradingview', 'metatrader', 'custom'
    signal_type VARCHAR(50) NOT NULL,  -- 'buy', 'sell', 'close'
    symbol VARCHAR(50),
    confidence DECIMAL(5, 4),
    payload JSONB,
    received_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    status VARCHAR(20)  -- 'pending', 'processed', 'rejected'
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_asset_registry_symbol ON asset_registry(symbol);
CREATE INDEX IF NOT EXISTS idx_tx_hash ON on_chain_transactions(tx_hash);
CREATE INDEX IF NOT EXISTS idx_wallet_balances_address ON wallet_balances(wallet_address);
CREATE INDEX IF NOT EXISTS idx_webhook_signals_status ON webhook_signals(status);
