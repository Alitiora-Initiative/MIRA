# MIRA Deployment Guide

## Overview

MIRA is a distributed multi-language microservices architecture. This guide covers deployment options for different components.

## Architecture Components

### Microservices
- **Wallet Service** (TypeScript): Port 50051 (gRPC), 8080 (WebSocket)
- **MEV Engine** (Rust): Port 50052 (gRPC)
- **Data Pipeline** (Go): Kafka consumers/producers
- **HFE Engine** (C++): Local execution (shared memory)
- **Portfolio Optimizer** (Julia): Port 8081 (HTTP)
- **Risk Simulation** (Julia): Port 8082 (HTTP)
- **Statistical Modeling** (R): Port 8083 (HTTP)
- **Pool Analytics** (R): Port 8084 (HTTP)
- **Backtesting Engine** (Java): Port 8085 (HTTP)
- **Trading Engine** (Python): Main orchestrator

### Infrastructure
- **Apache Kafka**: Port 9092
- **PostgreSQL**: Port 5432
- **Redis**: Port 6379

## Deployment Options

### 1. Docker Compose (Development/Testing)

```bash
# Start all infrastructure services
docker-compose up -d

# Start individual services
cd wallet-service && npm install && npm start
cd mev-engine && cargo run --release
cd data-pipeline/indexer && go run main.go
cd hfe-engine && cmake --build . && ./hfe_engine
cd analytics-julia && julia src/portfolio_optimizer.jl
cd analytics-r && Rscript src/statistical_modeling.R
cd backtesting-java && mvn spring-boot:run
cd trading-agent/python-engine && python main.py
```

### 2. Kubernetes (Production)

See `k8s/` directory for Kubernetes manifests (to be created).

### 3. Vercel (Documentation & Dashboard)

The documentation and dashboard can be deployed to Vercel:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### 4. Individual Cloud Platforms

**TypeScript Wallet Service:**
- Vercel / Railway / AWS Lambda

**Rust MEV Engine:**
- AWS EC2 / DigitalOcean / Railway

**Go Data Pipeline:**
- Kubernetes / AWS ECS / Google Cloud Run

**C++ HFE Engine:**
- Dedicated server (low latency requirements)

**Julia/R Analytics:**
- Kubernetes / AWS Batch

**Java Backtesting:**
- AWS EC2 / Google Cloud Run

**Python Core:**
- Heroku / Railway / AWS ECS

## Environment Variables

Create `.env` files for each service:

### Wallet Service (.env)
```
WALLET_GRPC_ENDPOINT=localhost:50051
WS_PORT=8080
SOLANA_RPC_URL=https://api.devnet.solana.com
EVM_RPC_URL=wss://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
```

### MEV Engine (.env)
```
MEV_GRPC_ENDPOINT=localhost:50052
MAX_SLIPPAGE_BPS=300
CIRCUIT_BREAKER_ENABLED=true
```

### Python Engine (.env)
```
WALLET_GRPC_ENDPOINT=localhost:50051
MEV_GRPC_ENDPOINT=localhost:50052
JULIA_PORTFOLIO_ENDPOINT=http://localhost:8081
JULIA_RISK_ENDPOINT=http://localhost:8082
R_STATISTICAL_ENDPOINT=http://localhost:8083
R_POOL_ENDPOINT=http://localhost:8084
BACKTESTING_ENDPOINT=http://localhost:8085
```

## Monitoring

- **Kafka UI**: http://localhost:8080 (if using docker-compose)
- **Service Logs**: Each service logs to stdout/stderr
- **Health Checks**: Each service provides `/health` endpoint

## Scaling

### Horizontal Scaling
- Go services: Scale by adding more instances
- Python services: Scale by adding more instances
- Julia/R services: Scale by adding more instances

### Vertical Scaling
- C++ HFE Engine: Requires dedicated CPU cores
- Rust MEV Engine: Requires high CPU performance

## Security

- All services should run behind a firewall
- Use HTTPS for all external communications
- Rotate API keys regularly
- Use secrets manager (AWS Secrets Manager, HashiCorp Vault)
- Enable authentication for all API endpoints

## Production Checklist

- [ ] All environment variables configured
- [ ] Database migrations run
- [ ] Kafka topics created
- [ ] SSL/TLS certificates installed
- [ ] Load balancer configured
- [ ] Monitoring and alerting set up
- [ ] Backup strategy in place
- [ ] Disaster recovery plan tested
- [ ] Security audit completed
- [ ] Performance testing completed
