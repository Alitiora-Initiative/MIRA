/**
 * Transaction Signer Service
 * Bridges between Python core and wallet signing
 * Handles both Solana and EVM transactions
 */

import { Connection, Keypair, PublicKey, Transaction } from '@solana/web3.js';
import { ethers, Signer } from 'ethers';
import { WalletManager } from './wallet-manager';

export interface SignRequest {
  walletAddress: string;
  transactionBytes: Buffer;
  chain: 'solana' | 'evm';
  biometricToken: string;
}

export interface SignResponse {
  success: boolean;
  signedTransaction?: Buffer;
  signature?: string;
  error?: string;
}

export class SignerService {
  private walletManager: WalletManager;
  private solanaConnection: Connection;
  private evmProviders: Map<string, ethers.JsonRpcProvider> = new Map();

  // In production, these would be stored in HSM
  private solanaKeypairs: Map<string, Keypair> = new Map();
  private evmWallets: Map<string, ethers.Wallet> = new Map();

  constructor(walletManager: WalletManager, solanaRpcUrl: string) {
    this.walletManager = walletManager;
    this.solanaConnection = new Connection(solanaRpcUrl, 'confirmed');
  }

  /**
   * Add EVM provider for a chain
   */
  addEvmProvider(chain: string, rpcUrl: string): void {
    this.evmProviders.set(chain, new ethers.JsonRpcProvider(rpcUrl));
  }

  /**
   * Register Solana keypair (in production, this would be HSM-backed)
   */
  registerSolanaKeypair(walletAddress: string, secretKey: Uint8Array): void {
    const keypair = Keypair.fromSecretKey(secretKey);
    if (keypair.publicKey.toBase58() !== walletAddress) {
      throw new Error('Solana keypair does not match wallet address');
    }
    this.solanaKeypairs.set(walletAddress, keypair);
  }

  /**
   * Register EVM wallet (in production, this would be HSM-backed)
   */
  registerEvmWallet(walletAddress: string, privateKey: string): void {
    const wallet = new ethers.Wallet(privateKey);
    if (wallet.address.toLowerCase() !== walletAddress.toLowerCase()) {
      throw new Error('EVM key does not match wallet address');
    }
    this.evmWallets.set(walletAddress, wallet);
  }

  /**
   * Sign transaction
   */
  async signTransaction(request: SignRequest): Promise<SignResponse> {
    try {
      // Validate biometric token
      if (!this.walletManager.validateBiometricToken(request.walletAddress, request.biometricToken)) {
        return { success: false, error: 'Invalid or expired biometric token' };
      }

      if (request.chain === 'solana') {
        return await this.signSolanaTransaction(request);
      } else if (request.chain === 'evm') {
        return await this.signEvmTransaction(request);
      } else {
        return { success: false, error: 'Unsupported chain' };
      }
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  }

  /**
   * Sign Solana transaction
   */
  private async signSolanaTransaction(request: SignRequest): Promise<SignResponse> {
    const keypair = this.solanaKeypairs.get(request.walletAddress);
    if (!keypair) {
      return { success: false, error: 'Solana keypair not registered' };
    }

    try {
      const transaction = Transaction.from(request.transactionBytes);
      transaction.sign(keypair);

      const signature = transaction.signature![0].toString('base64');
      const signedTransaction = transaction.serialize();

      return {
        success: true,
        signedTransaction: Buffer.from(signedTransaction),
        signature
      };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  }

  /**
   * Sign EVM transaction
   */
  private async signEvmTransaction(request: SignRequest): Promise<SignResponse> {
    const wallet = this.evmWallets.get(request.walletAddress);
    if (!wallet) {
      return { success: false, error: 'EVM wallet not registered' };
    }

    try {
      const tx = ethers.Transaction.from(request.transactionBytes);
      const signedTx = await wallet.signTransaction(tx);

      return {
        success: true,
        signedTransaction: Buffer.from(signedTx.serialized),
        signature: signedTx.hash
      };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  }

  /**
   * Broadcast transaction to network
   */
  async broadcastTransaction(walletAddress: string, signedTransaction: Buffer, chain: 'solana' | 'evm'): Promise<{ success: boolean; txHash?: string; error?: string }> {
    try {
      if (chain === 'solana') {
        const tx = Transaction.from(signedTransaction);
        const signature = await this.solanaConnection.sendRawTransaction(tx);
        return { success: true, txHash: signature };
      } else if (chain === 'evm') {
        // Determine which chain to use (simplified)
        const provider = this.evmProviders.get('ethereum');
        if (!provider) {
          return { success: false, error: 'EVM provider not configured' };
        }

        const txHash = await provider.broadcastTransaction(signedTransaction.toString('hex'));
        return { success: true, txHash };
      } else {
        return { success: false, error: 'Unsupported chain' };
      }
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  }

  /**
   * Get wallet balance
   */
  async getBalance(walletAddress: string, assetSymbol: string, chain: 'solana' | 'evm'): Promise<{ success: boolean; balance?: string; balanceUsd?: string; error?: string }> {
    try {
      if (chain === 'solana') {
        const publicKey = new PublicKey(walletAddress);
        const balance = await this.solanaConnection.getBalance(publicKey);
        const balanceSol = balance / 1e9;
        return {
          success: true,
          balance: balanceSol.toString(),
          balanceUsd: (balanceSol * 150).toString() // Simplified USD conversion
        };
      } else if (chain === 'evm') {
        const provider = this.evmProviders.get('ethereum');
        if (!provider) {
          return { success: false, error: 'EVM provider not configured' };
        }

        const balance = await provider.getBalance(walletAddress);
        const balanceEth = ethers.formatEther(balance);
        return {
          success: true,
          balance: balanceEth,
          balanceUsd: (parseFloat(balanceEth) * 2000).toString() // Simplified USD conversion
        };
      } else {
        return { success: false, error: 'Unsupported chain' };
      }
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  }
}
