/**
 * Wallet Service Main Entry Point
 * Starts gRPC server, WebSocket gateway, and manages wallet operations
 */

import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import { join } from 'path';
import { timingSafeEqual } from 'crypto';
import { WalletManager } from './wallet-manager';
import { SignerService } from './signer-service';
import { WsGateway } from './ws-gateway';
import * as dotenv from 'dotenv';

dotenv.config();

const PROTO_PATH = join(__dirname, '../proto/wallet.proto');
const PORT = process.env.GRPC_PORT || '50051';
const WS_PORT = process.env.WS_PORT || '8080';
const GRPC_HOST = process.env.MIRA_GRPC_HOST || '127.0.0.1';
const SOLANA_RPC_URL = process.env.SOLANA_RPC_URL || 'https://api.devnet.solana.com';

function authorized(call: { metadata: grpc.Metadata }): boolean {
  const expected = process.env.MIRA_WALLET_TOKEN || '';
  if (!expected) return false;
  const raw = call.metadata.get('authorization')[0];
  const presented = typeof raw === 'string' ? raw : Buffer.isBuffer(raw) ? raw.toString('utf8') : '';
  const token = presented.startsWith('Bearer ') ? presented.slice(7) : presented;
  const left = Buffer.from(token);
  const right = Buffer.from(expected);
  if (left.length !== right.length || left.length === 0) return false;
  return timingSafeEqual(left, right);
}

function deny(callback: (err: unknown, value: unknown) => void) {
  callback(null, { success: false, error: 'unauthorized' });
}

// Load protobuf
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
});

const walletProto = grpc.loadPackageDefinition(packageDefinition).wallet as any;

// Initialize services
const walletManager = new WalletManager();
const signerService = new SignerService(walletManager, SOLANA_RPC_URL);

const enrolledAddress = process.env.MIRA_WALLET_ADDRESS || '';
const enrolledPassword = process.env.MIRA_WALLET_PASSWORD || '';
if (enrolledAddress && enrolledPassword) {
  const enrolled = walletManager.enrollWallet(enrolledAddress, enrolledPassword);
  if (!enrolled.success) {
    console.error('Wallet enrollment failed:', enrolled.error);
  }
}

// Add EVM provider if configured
if (process.env.EVM_RPC_URL) {
  signerService.addEvmProvider('ethereum', process.env.EVM_RPC_URL);
}

// Start WebSocket gateway
const wsGateway = new WsGateway(parseInt(WS_PORT), walletManager, signerService);

// Implement gRPC service
const walletService = {
  GetWalletState: (call: any, callback: any) => {
    if (!authorized(call)) {
      deny(callback);
      return;
    }
    const { wallet_address } = call.request;
    const state = walletManager.getWalletState(wallet_address);

    if (!state) {
      callback(null, {
        is_locked: true,
        wallet_address: wallet_address,
        supported_chains: [],
        last_unlocked_timestamp: 0
      });
    } else {
      callback(null, {
        is_locked: state.isLocked,
        wallet_address: state.walletAddress,
        supported_chains: state.supportedChains,
        last_unlocked_timestamp: state.lastUnlockedTimestamp
      });
    }
  },

  SignTransaction: async (call: any, callback: any) => {
    if (!authorized(call)) {
      deny(callback);
      return;
    }
    const { wallet_address, transaction_bytes, chain, biometric_token } = call.request;

    const response = await signerService.signTransaction({
      walletAddress: wallet_address,
      transactionBytes: Buffer.from(transaction_bytes),
      chain,
      biometricToken: biometric_token
    });

    if (response.success) {
      callback(null, {
        success: true,
        signed_transaction: response.signedTransaction,
        signature: response.signature
      });

      // Push transaction confirmation via WebSocket
      if (response.signature) {
        wsGateway.pushTransactionConfirmation(wallet_address, response.signature, chain);
      }
    } else {
      callback(null, {
        success: false,
        error: response.error
      });
    }
  },

  GetBalance: async (call: any, callback: any) => {
    if (!authorized(call)) {
      deny(callback);
      return;
    }
    const { wallet_address, asset_symbol } = call.request;

    // Default to Solana for now
    const response = await signerService.getBalance(wallet_address, asset_symbol || 'SOL', 'solana');

    if (response.success) {
      callback(null, {
        success: true,
        balance: response.balance,
        balance_usd: response.balanceUsd
      });
    } else {
      callback(null, {
        success: false,
        error: response.error
      });
    }
  },

  BroadcastTransaction: async (call: any, callback: any) => {
    if (!authorized(call)) {
      deny(callback);
      return;
    }
    const { wallet_address, signed_transaction, chain } = call.request;

    const response = await signerService.broadcastTransaction(
      wallet_address,
      Buffer.from(signed_transaction),
      chain
    );

    if (response.success) {
      callback(null, {
        success: true,
        transaction_hash: response.txHash
      });
    } else {
      callback(null, {
        success: false,
        error: response.error
      });
    }
  },

  UnlockWallet: (call: any, callback: any) => {
    if (!authorized(call)) {
      deny(callback);
      return;
    }
    const { wallet_address, password } = call.request;

    const response = walletManager.unlockWallet(wallet_address, password);

    if (response.success) {
      callback(null, {
        success: true,
        session_token: response.sessionToken,
        biometric_token: response.biometricToken
      });

      // Push wallet status update
      wsGateway.pushWalletStatus(wallet_address);
    } else {
      callback(null, {
        success: false,
        error: response.error
      });
    }
  },

  LockWallet: (call: any, callback: any) => {
    if (!authorized(call)) {
      deny(callback);
      return;
    }
    const { wallet_address, session_token } = call.request;

    const response = walletManager.lockWallet(wallet_address, session_token);

    if (response.success) {
      callback(null, {
        success: true
      });

      // Push wallet status update
      wsGateway.pushWalletStatus(wallet_address);
    } else {
      callback(null, {
        success: false,
        error: response.error
      });
    }
  }
};

// Start gRPC server
const server = new grpc.Server();
server.addService(walletProto.WalletService.service, walletService);

server.bindAsync(
  `${GRPC_HOST}:${PORT}`,
  grpc.ServerCredentials.createInsecure(),
  (error: Error | null, port: number) => {
    if (error) {
      console.error('Failed to start gRPC server:', error);
      return;
    }

    console.log(`Wallet Service gRPC server running on ${GRPC_HOST}:${port}`);
    console.log(`WebSocket gateway running on 127.0.0.1:${WS_PORT}`);
  }
);

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('Shutting down gracefully...');
  wsGateway.stop();
  server.tryShutdown(() => {
    console.log('Server shutdown complete');
    process.exit(0);
  });
});
