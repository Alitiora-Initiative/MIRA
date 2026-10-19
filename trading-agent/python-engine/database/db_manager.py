"""
Database Manager - Handles data persistence for MIRA.
"""

from typing import Dict, Any
from loguru import logger
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from core.config import Config

Base = declarative_base()


class Trade(Base):
    """Trade model."""
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    token_address = Column(String)
    input_mint = Column(String)
    output_mint = Column(String)
    amount = Column(Float)
    phi_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String)


class DBManager:
    """Manages database operations."""

    def __init__(self, config: Config):
        self.config = config
        self.engine = None
        self.Session = None
        logger.info("Database Manager initialized")

    async def initialize(self):
        """Initialize database connection."""
        logger.info("Initializing database...")

        try:
            self.engine = create_engine(self.config.database.connection_string)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    async def log_trade(self, signal: Dict[str, Any], result: Dict[str, Any]):
        """Log a trade to the database."""
        try:
            session = self.Session()

            trade = Trade(
                token_address=signal.get('token_address'),
                input_mint=signal.get('input_mint'),
                output_mint=signal.get('output_mint'),
                amount=signal.get('amount'),
                phi_score=signal.get('phi_score'),
                status='executed' if result.get('success') else 'failed'
            )

            session.add(trade)
            session.commit()

            logger.info(f"Trade logged: {signal.get('token_address')}")

        except Exception as e:
            logger.error(f"Error logging trade: {e}")
        finally:
            if 'session' in locals() and session is not None:
                session.close()

    async def get_trades(self, limit: int = 100) -> list:
        """Get recent trades from database."""
        try:
            session = self.Session()
            trades = session.query(Trade).order_by(Trade.timestamp.desc()).limit(limit).all()

            return [
                {
                    'id': t.id,
                    'token_address': t.token_address,
                    'input_mint': t.input_mint,
                    'output_mint': t.output_mint,
                    'amount': t.amount,
                    'phi_score': t.phi_score,
                    'timestamp': t.timestamp.isoformat() if t.timestamp else None,
                    'status': t.status
                }
                for t in trades
            ]

        except Exception as e:
            logger.error(f"Error getting trades: {e}")
            return []
        finally:
            if 'session' in locals() and session is not None:
                session.close()

    async def shutdown(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


# Engine and older callers import this name. The class itself used to be only DBManager,
# so `from database.db_manager import DatabaseManager` crashed on startup.
DatabaseManager = DBManager
