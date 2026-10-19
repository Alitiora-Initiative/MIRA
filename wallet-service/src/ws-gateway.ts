/**
 * WebSocket Gateway
 * Real-time communication with dashboard
 * Streams wallet balance updates, transaction confirmations, and status changes
 */

import { WebSocketServer, WebSocket } from 'ws';
import { timingSafeEqual } from 'crypto';
import { WalletManager } from './wallet-manager';
import { SignerService } from './signer-service';

export type WsChannel = 'wallet:balance' | 'wallet:transaction' | 'wallet:status';

export interface WsMessage {
  channel: WsChannel;
  data: any;
  timestamp: number;
}

export class WsGateway {
  private wss: WebSocketServer;
  private walletManager: WalletManager;
  private signerService: SignerService;
  private clients: Set<WebSocket> = new Set();
  private balanceUpdateInterval: NodeJS.Timeout | null = null;

  constructor(port: number, walletManager: WalletManager, signerService: SignerService) {
    this.walletManager = walletManager;
    this.signerService = signerService;
    this.wss = new WebSocketServer({ host: '127.0.0.1', port });

    this.wss.on('connection', (ws: WebSocket) => {
      this.clients.add(ws);
      console.log('WebSocket client connected');

      ws.on('message', (message: string) => {
        try {
          const data = JSON.parse(message);
          this.handleClientMessage(ws, data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      });

      ws.on('close', () => {
        this.clients.delete(ws);
        console.log('WebSocket client disconnected');
      });

      ws.on('error', (error) => {
        console.error('WebSocket error:', error);
        this.clients.delete(ws);
      });
    });

    console.log(`WebSocket gateway started on port ${port}`);
    this.startBalanceUpdates();
  }

  private clientAllowed(data: { authToken?: string }): boolean {
    const expected = process.env.MIRA_WS_TOKEN || '';
    const presented = data.authToken || '';
    if (!expected || !presented) return false;
    const left = Buffer.from(presented);
    const right = Buffer.from(expected);
    if (left.length !== right.length) return false;
    return timingSafeEqual(left, right);
  }

  /**
   * Handle messages from clients. Secrets are never echoed back.
   */
  private handleClientMessage(ws: WebSocket, data: any): void {
    if (!this.clientAllowed(data)) {
      ws.close(4001, 'unauthorized');
      return;
    }
    const { action, walletAddress } = data;

    switch (action) {
      case 'subscribe':
        this.sendToClient(ws, {
          channel: 'wallet:status',
          data: this.walletManager.toPublic(this.walletManager.getWalletState(walletAddress)),
          timestamp: Date.now()
        });
        break;

      case 'get_balance':
        this.pushBalanceUpdate(walletAddress);
        break;

      default:
        console.log('Unknown action');
    }
  }

  /**
   * Send message to specific client
   */
  private sendToClient(ws: WebSocket, message: WsMessage): void {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    }
  }

  /**
   * Broadcast message to all clients
   */
  broadcast(message: WsMessage): void {
    const messageStr = JSON.stringify(message);
    for (const client of this.clients) {
      if (client.readyState === WebSocket.OPEN) {
        client.send(messageStr);
      }
    }
  }

  /**
   * Start periodic balance updates
   */
  private startBalanceUpdates(): void {
    this.balanceUpdateInterval = setInterval(() => {
      this.walletManager.cleanupExpiredSessions();
      // In production, push balance updates for all unlocked wallets
    }, 30000); // Every 30 seconds
  }

  /**
   * Push balance update for a wallet
   */
  async pushBalanceUpdate(walletAddress: string): Promise<void> {
    const walletState = this.walletManager.getWalletState(walletAddress);
    if (!walletState || walletState.isLocked) {
      return;
    }

    try {
      const solBalance = await this.signerService.getBalance(walletAddress, 'SOL', 'solana');
      if (solBalance.success) {
        this.broadcast({
          channel: 'wallet:balance',
          data: {
            walletAddress,
            asset: 'SOL',
            balance: solBalance.balance,
            balanceUsd: solBalance.balanceUsd
          },
          timestamp: Date.now()
        });
      }
    } catch (error) {
      console.error('Error pushing balance update:', error);
    }
  }

  /**
   * Push transaction confirmation
   */
  pushTransactionConfirmation(walletAddress: string, txHash: string, chain: string): void {
    this.broadcast({
      channel: 'wallet:transaction',
      data: {
        walletAddress,
        txHash,
        chain,
        status: 'confirmed'
      },
      timestamp: Date.now()
    });
  }

  /**
   * Push wallet status change
   */
  pushWalletStatus(walletAddress: string): void {
    const walletState = this.walletManager.getWalletState(walletAddress);
    if (walletState) {
      this.broadcast({
        channel: 'wallet:status',
        data: this.walletManager.toPublic(walletState),
        timestamp: Date.now()
      });
    }
  }

  /**
   * Stop the gateway
   */
  stop(): void {
    if (this.balanceUpdateInterval) {
      clearInterval(this.balanceUpdateInterval);
    }
    this.wss.close();
    console.log('WebSocket gateway stopped');
  }
}
