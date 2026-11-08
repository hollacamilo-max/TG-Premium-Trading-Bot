import os
from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Bot Configuration
    BOT_TOKEN: str = Field(..., description="Telegram Bot Token from @BotFather")
    ADMIN_IDS: List[int] = Field(default_factory=list, description="List of admin Telegram user IDs")

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/trading_bot",
        description="PostgreSQL connection URL"
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for caching and sessions"
    )

    # EVM Chain RPC URLs
    ETHEREUM_RPC: str = Field(default="https://eth.llamarpc.com", description="Ethereum RPC URL")
    BASE_RPC: str = Field(default="https://mainnet.base.org", description="Base RPC URL")
    ARBITRUM_RPC: str = Field(default="https://arb1.arbitrum.io/rpc", description="Arbitrum RPC URL")
    BSC_RPC: str = Field(default="https://bsc-dataseed.binance.org", description="BSC RPC URL")
    POLYGON_RPC: str = Field(default="https://polygon-rpc.com", description="Polygon RPC URL")
    AVALANCHE_RPC: str = Field(default="https://api.avax.network/ext/bc/C/rpc", description="Avalanche RPC URL")

    # Solana RPC
    SOLANA_RPC: str = Field(default="https://api.mainnet-beta.solana.com", description="Solana RPC URL")
    SOLANA_WS: str = Field(default="wss://api.mainnet-beta.solana.com", description="Solana WebSocket URL")

    # DEX Router Addresses (EVM)
    UNISWAP_V2_ROUTER: str = Field(default="0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D", description="Uniswap V2 Router")
    UNISWAP_V3_ROUTER: str = Field(default="0xE592427A0AEce92De3Edee1F18E0157C05861564", description="Uniswap V3 Router")
    ONEINCH_ROUTER: str = Field(default="0x1111111254EEB25477B68fb85Ed929f73A960582", description="1inch Router")

    # Solana DEX Programs
    JUPITER_PROGRAM_ID: str = Field(default="JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4", description="Jupiter Program ID")
    RAYDIUM_PROGRAM_ID: str = Field(default="675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8", description="Raydium Program ID")

    # Security
    ENCRYPTION_KEY: str = Field(..., description="32-byte encryption key for wallet data (base64 encoded)")
    SESSION_SECRET: str = Field(..., description="Secret for session signing")

    # Trading Settings
    DEFAULT_SLIPPAGE: float = Field(default=1.0, description="Default slippage percentage")
    MAX_SLIPPAGE: float = Field(default=50.0, description="Maximum allowed slippage")
    MIN_TRADE_AMOUNT_USD: float = Field(default=5.0, description="Minimum trade amount in USD")
    MAX_TRADE_AMOUNT_USD: float = Field(default=100000.0, description="Maximum trade amount in USD")
    GAS_MULTIPLIER: float = Field(default=1.2, description="Gas price multiplier for faster confirmation")
    PRIORITY_FEE_SOL: float = Field(default=0.0001, description="Priority fee for Solana in SOL")

    # Referral System
    REFERRAL_COMMISSION_BPS: int = Field(default=100, description="Referral commission in basis points (1% = 100)")
    REFERRAL_TIER_2_BPS: int = Field(default=20, description="Tier 2 referral commission in basis points")

    # Monitoring
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")

    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v

    @field_validator("ENCRYPTION_KEY")
    @classmethod
    def validate_encryption_key(cls, v):
        import base64
        try:
            decoded = base64.b64decode(v)
            if len(decoded) != 32:
                raise ValueError("Encryption key must be 32 bytes (base64 encoded)")
        except Exception:
            raise ValueError("Invalid base64 encryption key")
        return v

    def get_evm_rpc(self, chain: str) -> str:
        """Get RPC URL for EVM chain."""
        chain = chain.lower()
        rpc_map = {
            "ethereum": self.ETHEREUM_RPC,
            "eth": self.ETHEREUM_RPC,
            "base": self.BASE_RPC,
            "arbitrum": self.ARBITRUM_RPC,
            "arb": self.ARBITRUM_RPC,
            "bsc": self.BSC_RPC,
            "polygon": self.POLYGON_RPC,
            "matic": self.POLYGON_RPC,
            "avalanche": self.AVALANCHE_RPC,
            "avax": self.AVALANCHE_RPC,
        }
        return rpc_map.get(chain, self.ETHEREUM_RPC)

    def get_chain_id(self, chain: str) -> int:
        """Get chain ID for EVM chain."""
        chain = chain.lower()
        chain_ids = {
            "ethereum": 1,
            "eth": 1,
            "base": 8453,
            "arbitrum": 42161,
            "arb": 42161,
            "bsc": 56,
            "polygon": 137,
            "matic": 137,
            "avalanche": 43114,
            "avax": 43114,
        }
        return chain_ids.get(chain, 1)


@lru_cache
def get_settings() -> Settings:
    return Settings()
