"""
gRPC client for Wallet Service
Interfaces with TypeScript wallet service for secure transaction signing
"""

import grpc
from typing import Optional, Dict, Any
from loguru import logger
import os

# Import generated protobuf classes
# These will be generated from wallet.proto
try:
    from wallet_pb2 import (
        WalletRequest,
        WalletState,
        SignRequest,
        SignResponse,
        BalanceRequest,
        BalanceResponse,
        TxRequest,
        TxResponse,
        UnlockRequest,
        UnlockResponse,
        LockRequest,
        LockResponse
    )
    from wallet_pb2_grpc import WalletServiceStub
except ImportError:
    logger.warning("Protobuf files not generated yet. Run: cd wallet-service && npm run proto")
    # Create stub classes for development
    class WalletRequest:
        pass
    class WalletState:
        pass
    class SignRequest:
        pass
    class SignResponse:
        pass
    class BalanceRequest:
        pass
    class BalanceResponse:
        pass
    class TxRequest:
        pass
    class TxResponse:
        pass
    class UnlockRequest:
        pass
    class UnlockResponse:
        pass
    class LockRequest:
        pass
    class LockResponse:
        pass
    class WalletServiceStub:
        pass


class WalletClient:
    """gRPC client for wallet service operations."""

    def __init__(self, grpc_endpoint: str = None):
        """
        Initialize wallet client.

        Args:
            grpc_endpoint: gRPC server address (default from env or localhost:50051)
        """
        self.grpc_endpoint = grpc_endpoint or os.getenv('WALLET_GRPC_ENDPOINT', 'localhost:50051')
        self.channel = None
        self.stub = None
        self._connect()

    def _connect(self):
        """Establish gRPC connection."""
        try:
            self.channel = grpc.insecure_channel(self.grpc_endpoint)
            self.stub = WalletServiceStub(self.channel)
            logger.info(f"Connected to wallet service at {self.grpc_endpoint}")
        except Exception as e:
            logger.error(f"Failed to connect to wallet service: {e}")
            raise

    def reconnect(self):
        """Reconnect to wallet service."""
        if self.channel:
            self.channel.close()
        self._connect()

    def get_wallet_state(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        """
        Get wallet state.

        Args:
            wallet_address: Wallet public key

        Returns:
            Wallet state dict or None
        """
        try:
            request = WalletRequest(wallet_address=wallet_address)
            response = self.stub.GetWalletState(request)

            return {
                'is_locked': response.is_locked,
                'wallet_address': response.wallet_address,
                'supported_chains': list(response.supported_chains),
                'last_unlocked_timestamp': response.last_unlocked_timestamp
            }
        except Exception as e:
            logger.error(f"Error getting wallet state: {e}")
            return None

    def unlock_wallet(
        self,
        wallet_address: str,
        password: str
    ) -> Optional[Dict[str, Any]]:
        """
        Unlock wallet and get session/biometric tokens.

        Args:
            wallet_address: Wallet public key
            password: Wallet password

        Returns:
            Response with session_token and biometric_token or None
        """
        try:
            request = UnlockRequest(
                wallet_address=wallet_address,
                password=password
            )
            response = self.stub.UnlockWallet(request)

            if response.success:
                return {
                    'success': True,
                    'session_token': response.session_token,
                    'biometric_token': response.biometric_token
                }
            else:
                return {
                    'success': False,
                    'error': response.error
                }
        except Exception as e:
            logger.error(f"Error unlocking wallet: {e}")
            return None

    def lock_wallet(
        self,
        wallet_address: str,
        session_token: str
    ) -> bool:
        """
        Lock wallet.

        Args:
            wallet_address: Wallet public key
            session_token: Session token from unlock

        Returns:
            True if successful
        """
        try:
            request = LockRequest(
                wallet_address=wallet_address,
                session_token=session_token
            )
            response = self.stub.LockWallet(request)
            return response.success
        except Exception as e:
            logger.error(f"Error locking wallet: {e}")
            return False

    def sign_transaction(
        self,
        wallet_address: str,
        transaction_bytes: bytes,
        chain: str,
        biometric_token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Sign transaction via wallet service.

        Args:
            wallet_address: Wallet public key
            transaction_bytes: Unsigned transaction bytes
            chain: 'solana' or 'evm'
            biometric_token: Biometric token from unlock

        Returns:
            Response with signed_transaction and signature or None
        """
        try:
            request = SignRequest(
                wallet_address=wallet_address,
                transaction_bytes=transaction_bytes,
                chain=chain,
                biometric_token=biometric_token
            )
            response = self.stub.SignTransaction(request)

            if response.success:
                return {
                    'success': True,
                    'signed_transaction': response.signed_transaction,
                    'signature': response.signature
                }
            else:
                return {
                    'success': False,
                    'error': response.error
                }
        except Exception as e:
            logger.error(f"Error signing transaction: {e}")
            return None

    def get_balance(
        self,
        wallet_address: str,
        asset_symbol: str = 'SOL'
    ) -> Optional[Dict[str, Any]]:
        """
        Get wallet balance.

        Args:
            wallet_address: Wallet public key
            asset_symbol: Asset symbol (default: SOL)

        Returns:
            Response with balance and balance_usd or None
        """
        try:
            request = BalanceRequest(
                wallet_address=wallet_address,
                asset_symbol=asset_symbol
            )
            response = self.stub.GetBalance(request)

            if response.success:
                return {
                    'success': True,
                    'balance': response.balance,
                    'balance_usd': response.balance_usd
                }
            else:
                return {
                    'success': False,
                    'error': response.error
                }
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return None

    def broadcast_transaction(
        self,
        wallet_address: str,
        signed_transaction: bytes,
        chain: str
    ) -> Optional[Dict[str, Any]]:
        """
        Broadcast signed transaction to network.

        Args:
            wallet_address: Wallet public key
            signed_transaction: Signed transaction bytes
            chain: 'solana' or 'evm'

        Returns:
            Response with transaction_hash or None
        """
        try:
            request = TxRequest(
                wallet_address=wallet_address,
                signed_transaction=signed_transaction,
                chain=chain
            )
            response = self.stub.BroadcastTransaction(request)

            if response.success:
                return {
                    'success': True,
                    'transaction_hash': response.transaction_hash
                }
            else:
                return {
                    'success': False,
                    'error': response.error
                }
        except Exception as e:
            logger.error(f"Error broadcasting transaction: {e}")
            return None

    def close(self):
        """Close gRPC connection."""
        if self.channel:
            self.channel.close()
            logger.info("Wallet client connection closed")
