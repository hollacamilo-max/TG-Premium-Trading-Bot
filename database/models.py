import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base


class ChainType(str, enum.Enum):
    EVM = "evm"
    SOLANA = "solana"
    TON = "ton"


class WalletType(str, enum.Enum):
    SEED_PHRASE = "seed_phrase"
    PRIVATE_KEY = "private_key"


class TradeStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TradeType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"
    SWAP = "swap"
    LIMIT_BUY = "limit_buy"
    LIMIT_SELL = "limit_sell"
    COPY_TRADE = "copy_trade"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user ID
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    language_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    referred_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True, index=True)
    referral_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    total_volume_usd: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    total_trades: Mapped[int] = mapped_column(Integer, default=0)
    commission_earned_usd: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    settings: Mapped[dict] = mapped_column(default_factory=dict)  # JSON settings
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    wallets: Mapped[list["Wallet"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    trades: Mapped[list["Trade"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    referrals: Mapped[list["Referral"]] = relationship(back_populates="referrer", foreign_keys="Referral.referrer_id")
    referred_by_rel: Mapped[Optional["Referral"]] = relationship(back_populates="referred", foreign_keys="Referral.referred_id")
    admin_logs: Mapped[list["AdminLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_users_referred_by_created", "referred_by", "created_at"),
    )


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    chain: Mapped[ChainType] = mapped_column(Enum(ChainType), index=True)
    address: Mapped[str] = mapped_column(String(255), index=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # User-defined name
    wallet_type: Mapped[WalletType] = mapped_column(Enum(WalletType))
    encrypted_data: Mapped[str] = mapped_column(Text)  # Encrypted seed phrase or private key
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    balance_cache: Mapped[dict] = mapped_column(default_factory=dict)  # Cached balances
    last_balance_update: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship(back_populates="wallets")
    trades: Mapped[list["Trade"]] = relationship(back_populates="wallet", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("user_id", "chain", "address", name="uq_user_chain_address"),
        Index("ix_wallets_user_chain_active", "user_id", "chain", "is_active"),
    )


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    wallet_id: Mapped[int] = mapped_column(Integer, ForeignKey("wallets.id", ondelete="CASCADE"), index=True)
    chain: Mapped[ChainType] = mapped_column(Enum(ChainType), index=True)
    trade_type: Mapped[TradeType] = mapped_column(Enum(TradeType))
    status: Mapped[TradeStatus] = mapped_column(Enum(TradeStatus), default=TradeStatus.PENDING, index=True)

    # Token info
    token_in_address: Mapped[str] = mapped_column(String(255))
    token_in_symbol: Mapped[str] = mapped_column(String(50))
    token_in_decimals: Mapped[int] = mapped_column(Integer)
    token_out_address: Mapped[str] = mapped_column(String(255))
    token_out_symbol: Mapped[str] = mapped_column(String(50))
    token_out_decimals: Mapped[int] = mapped_column(Integer)

    # Amounts
    amount_in: Mapped[Decimal] = mapped_column(Numeric(38, 18))
    amount_out_min: Mapped[Decimal] = mapped_column(Numeric(38, 18))
    amount_out_actual: Mapped[Optional[Decimal]] = mapped_column(Numeric(38, 18), nullable=True)
    price_impact: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Transaction info
    tx_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    block_number: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    gas_used: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    gas_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(38, 18), nullable=True)
    fees_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)

    # DEX info
    dex_name: Mapped[str] = mapped_column(String(50))
    dex_router: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    route: Mapped[Optional[dict]] = mapped_column(default_factory=dict)  # Swap route details

    # Error info
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship(back_populates="trades")
    wallet: Mapped["Wallet"] = relationship(back_populates="trades")

    __table_args__ = (
        Index("ix_trades_user_status_created", "user_id", "status", "created_at"),
        Index("ix_trades_wallet_created", "wallet_id", "created_at"),
        Index("ix_trades_tx_hash", "tx_hash"),
    )


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    referrer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    referred_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    tier: Mapped[int] = mapped_column(Integer, default=1)  # 1 = direct, 2 = indirect
    commission_bps: Mapped[int] = mapped_column(Integer)
    total_commission_usd: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    total_volume_usd: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    referrer: Mapped["User"] = relationship(back_populates="referrals", foreign_keys=[referrer_id])
    referred: Mapped["User"] = relationship(back_populates="referred_by_rel", foreign_keys=[referred_id])

    __table_args__ = (
        UniqueConstraint("referrer_id", "referred_id", name="uq_referrer_referred"),
        Index("ix_referrals_referrer_active", "referrer_id", "is_active"),
    )


class AdminLog(Base):
    __tablename__ = "admin_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    admin_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)  # Admin who viewed
    action: Mapped[str] = mapped_column(String(100), index=True)  # e.g., "wallet_import", "message", "command", "trade"
    details: Mapped[dict] = mapped_column(default_factory=dict)  # Full details including sensitive data
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="admin_logs")

    __table_args__ = (
        Index("ix_admin_logs_user_action_created", "user_id", "action", "created_at"),
        Index("ix_admin_logs_admin_created", "admin_id", "created_at"),
    )


class BotSettings(Base):
    __tablename__ = "bot_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[dict] = mapped_column(default_factory=dict)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
