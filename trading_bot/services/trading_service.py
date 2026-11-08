@import json
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from config import get_settings
from utils.encryption import encrypt_data, decrypt_data
from utils.helpers import format_usd, format_token_amount
from database.models import Trade, TradeStatus, TradeType, ChainType, Wallet
from database.base import get_db
from services.wallet_service import WalletService


class TradingService:
    def __init__(self):
        self.settings = get_settings()
        self.wallet_service = WalletService()
    
    async def execute_swap(
        self,
        user_id: int,
        wallet: Wallet,
        token_in_address: str,
        token_in_symbol: str,
        token_in_decimals: int,
        token_out_address: str,
        token_out_symbol: str,
        token_out_decimals: int,
        amount_in: Decimal,
        slippage: float,
        trade_type: TradeType = TradeType.SWAP,
        dex_name: str = "auto",
    ) -> Trade:
        """Execute a token swap."""
        from sqlalchemy import select
        
        # Calculate minimum output amount based on slippage
        # This is simplified - in production, you would query DEX for quotes
        amount_out_min = amount_in * Decimal(str(1 - slippage / 100))
        
        # Create trade record
        trade = Trade(
            user_id=user_id,
            wallet_id=wallet.id,
            chain=wallet.chain,
            trade_type=trade_type,
            status=TradeStatus.PENDING,
            token_in_address=token_in_address,
            token_in_symbol=token_in_symbol,
            token_in_decimals=token_in_decimals,
            token_out_address=token_out_address,
            token_out_symbol=token_out_symbol,
            token_out_decimals=token_out_decimals,
            amount_in=amount_in,
            amount_out_min=amount_out_min,
            dex_name=dex_name,
            price_impact=None,
        )
        
        async with get_db() as session:
            session.add(trade)
            await session.flush()
            await session.refresh(trade)
        
        # TODO: Actually execute the swap based on chain and DEX
        # This would involve:
        # 1. Getting quotes from DEX (Jupiter for Solana, 1inch/Uniswap for EVM)
        # 2. Building transaction
        # 3. Signing with wallet private key
        # 4. Broadcasting transaction
        # 5. Updating trade status
        
        return trade
    
    async def execute_evm_swap(
        self,
        trade: Trade,
        wallet: Wallet,
        private_key: str,
    ) -> Trade:
        """Execute EVM swap via DEX."""
        # This is a placeholder for actual DEX integration
        # Would integrate with 1inch, Uniswap, etc.
        trade.status = TradeStatus.CONFIRMED
        trade.confirmed_at = datetime.utcnow()
        trade.tx_hash = "0x" + "0" * 64  # Placeholder
        return trade
    
    async def execute_solana_swap(
        self,
        trade: Trade,
        wallet: Wallet,
        private_key: str,
    ) -> Trade:
        """Execute Solana swap via Jupiter."""
        # This is a placeholder for actual Jupiter integration
        trade.status = TradeStatus.CONFIRMED
        trade.confirmed_at = datetime.utcnow()
        trade.tx_hash = "solana_tx_placeholder"
        return trade
    
    async def get_token_price(self, chain: str, token_address: str) -> Optional[Decimal]:
        """Get token price in USD."""
        # Placeholder - would integrate with price APIs (CoinGecko, DexScreener, etc.)
        return None
    
    async def get_token_info(self, chain: str, token_address: str) -> Optional[Dict[str, Any]]:
        """Get token info (symbol, decimals, name)."""
        # Placeholder - would query token contract
        return None
    
    async def estimate_gas(self, chain: str, tx_data: dict) -> int:
        """Estimate gas for EVM transaction."""
        # Placeholder
        return 300000
    
    async def get_user_trades(
        self,
        user_id: int,
        status: Optional[TradeStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Trade]:
        """Get user trade history."""
        from sqlalchemy import select
        async with get_db() as session:
            query = select(Trade).where(Trade.user_id == user_id)
            if status:
                query = query.where(Trade.status == status)
            query = query.order_by(Trade.created_at.desc()).limit(limit).offset(offset)
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def get_trade(self, trade_id: int, user_id: int) -> Optional[Trade]:
        """Get specific trade."""
        from sqlalchemy import select
        async with get_db() as session:
            result = await session.execute(
                select(Trade).where(Trade.id == trade_id, Trade.user_id == user_id)
            )
            return result.scalar_one_or_none()
    
    async def update_trade_status(
        self,
        trade_id: int,
        status: TradeStatus,
        tx_hash: Optional[str] = None,
        amount_out_actual: Optional[Decimal] = None,
        gas_used: Optional[int] = None,
        gas_price: Optional[Decimal] = None,
        fees_usd: Optional[Decimal] = None,
        error_message: Optional[str] = None,
    ) -> Optional[Trade]:
        """Update trade status."""
        from sqlalchemy import select, update
        async with get_db() as session:
            trade = await session.execute(
                select(Trade).where(Trade.id == trade_id)
            )
            trade = trade.scalar_one_or_none()
            if not trade:
                return None
            
            trade.status = status
            if tx_hash:
                trade.tx_hash = tx_hash
            if amount_out_actual:
                trade.amount_out_actual = amount_out_actual
            if gas_used:
                trade.gas_used = gas_used
            if gas_price:
                trade.gas_price = gas_price
            if fees_usd:
                trade.fees_usd = fees_usd
            if error_message:
                trade.error_message = error_message
            if status == TradeStatus.CONFIRMED:
                trade.confirmed_at = datetime.utcnow()
            
            await session.flush()
            await session.refresh(trade)
            return trade
