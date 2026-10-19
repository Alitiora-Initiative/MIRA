/**
 * Wallet State Manager
 * Manages wallet connection state, biometric tokens, and session management
 */

import { v4 as uuidv4 } from 'uuid';
import { randomBytes, scryptSync, timingSafeEqual } from 'crypto';

export interface PublicWalletState {
  isLocked: boolean;
  walletAddress: string;
  supportedChains: string[];
  lastUnlockedTimestamp: number;
}

interface PasswordVerifier {
  salt: Buffer;
  hash: Buffer;
}

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
  private verifiers: Map<string, PasswordVerifier> = new Map();
  private sessionTimeout: number = 300000; // 5 minutes
  private biometricTimeout: number = 60000; // 1 minute

  /**
   * Enroll a wallet password. Unlock fails closed until this succeeds.
   * The password is stored only as a scrypt hash.
   */
  enrollWallet(walletAddress: string, password: string): { success: boolean; error?: string } {
    if (!walletAddress || !/^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(walletAddress)) {
      return { success: false, error: 'Invalid wallet address' };
    }
    if (!password || password.length < 12) {
      return { success: false, error: 'Password must be at least 12 characters' };
    }
    const salt = randomBytes(16);
    const hash = scryptSync(password, salt, 32);
    this.verifiers.set(walletAddress, { salt, hash });
    this.getOrCreateWallet(walletAddress);
    return { success: true };
  }

  toPublic(wallet: WalletState | null): PublicWalletState | null {
    if (!wallet) return null;
    return {
      isLocked: wallet.isLocked,
      walletAddress: wallet.walletAddress,
      supportedChains: wallet.supportedChains,
      lastUnlockedTimestamp: wallet.lastUnlockedTimestamp,
    };
  }

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
    const verifier = this.verifiers.get(walletAddress);
    if (!verifier) {
      return { success: false, error: 'Wallet is not enrolled' };
    }
    if (!password) {
      return { success: false, error: 'Invalid password' };
    }

    const hash = scryptSync(password, verifier.salt, 32);
    if (hash.length !== verifier.hash.length || !timingSafeEqual(hash, verifier.hash)) {
      return { success: false, error: 'Invalid password' };
    }

    const wallet = this.getOrCreateWallet(walletAddress);
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
