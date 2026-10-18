/**
 * Wallet State Manager
 * Manages wallet connection state, biometric tokens, and session management
 */

import { v4 as uuidv4 } from 'uuid';

export interface WalletState {
  isLocked: boolean;
  walletAddress: string;
  supportedChains: string[];
  lastUnlockedTimestamp: number;
  sessionToken?: string;
  biometricToken?: string;
}

export class WalletManager {
  private wallets: Map<string, WalletState> = new Map();
  private sessionTimeout: number = 300000; // 5 minutes
  private biometricTimeout: number = 60000; // 1 minute

  /**
   * Create or get wallet state
   */
  getOrCreateWallet(walletAddress: string): WalletState {
    if (!this.wallets.has(walletAddress)) {
      const state: WalletState = {
        isLocked: true,
        walletAddress,
        supportedChains: ['solana', 'evm'],
        lastUnlockedTimestamp: 0
      };
      this.wallets.set(walletAddress, state);
    }
    return this.wallets.get(walletAddress)!;
  }

  /**
   * Unlock wallet with password and generate biometric token
   */
  unlockWallet(walletAddress: string, password: string): { success: boolean; sessionToken?: string; biometricToken?: string; error?: string } {
    const wallet = this.getOrCreateWallet(walletAddress);

    // In production, validate password against encrypted storage
    // For now, we'll accept any non-empty password
    if (!password || password.length < 8) {
      return { success: false, error: 'Invalid password' };
    }

    const sessionToken = uuidv4();
    const biometricToken = uuidv4();

    wallet.isLocked = false;
    wallet.sessionToken = sessionToken;
    wallet.biometricToken = biometricToken;
    wallet.lastUnlockedTimestamp = Date.now();

    return { success: true, sessionToken, biometricToken };
  }

  /**
   * Lock wallet
   */
  lockWallet(walletAddress: string, sessionToken: string): { success: boolean; error?: string } {
    const wallet = this.wallets.get(walletAddress);
    if (!wallet) {
      return { success: false, error: 'Wallet not found' };
    }

    if (wallet.sessionToken !== sessionToken) {
      return { success: false, error: 'Invalid session token' };
    }

    wallet.isLocked = true;
    wallet.sessionToken = undefined;
    wallet.biometricToken = undefined;

    return { success: true };
  }

  /**
   * Validate biometric token
   */
  validateBiometricToken(walletAddress: string, biometricToken: string): boolean {
    const wallet = this.wallets.get(walletAddress);
    if (!wallet || wallet.isLocked) {
      return false;
    }

    // Check token expiration
    if (Date.now() - wallet.lastUnlockedTimestamp > this.biometricTimeout) {
      wallet.isLocked = true;
      return false;
    }

    return wallet.biometricToken === biometricToken;
  }

  /**
   * Validate session token
   */
  validateSessionToken(walletAddress: string, sessionToken: string): boolean {
    const wallet = this.wallets.get(walletAddress);
    if (!wallet || wallet.isLocked) {
      return false;
    }

    // Check session expiration
    if (Date.now() - wallet.lastUnlockedTimestamp > this.sessionTimeout) {
      wallet.isLocked = true;
      return false;
    }

    return wallet.sessionToken === sessionToken;
  }

  /**
   * Get wallet state
   */
  getWalletState(walletAddress: string): WalletState | null {
    const wallet = this.wallets.get(walletAddress);
    if (!wallet) {
      return null;
    }

    // Auto-lock if session expired
    if (!wallet.isLocked && Date.now() - wallet.lastUnlockedTimestamp > this.sessionTimeout) {
      wallet.isLocked = true;
      wallet.sessionToken = undefined;
      wallet.biometricToken = undefined;
    }

    return wallet;
  }

  /**
   * Clean up expired sessions
   */
  cleanupExpiredSessions(): void {
    const now = Date.now();
    for (const [address, wallet] of this.wallets.entries()) {
      if (!wallet.isLocked && now - wallet.lastUnlockedTimestamp > this.sessionTimeout) {
        wallet.isLocked = true;
        wallet.sessionToken = undefined;
        wallet.biometricToken = undefined;
      }
    }
  }
}
