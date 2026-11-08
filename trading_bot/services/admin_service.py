@import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from config import get_settings
from database.models import AdminLog, User, Trade, Wallet
from database.base import get_db
from sqlalchemy import select, func, desc


class AdminService:
    def __init__(self):
        self.settings = get_settings()
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is an admin."""
        return user_id in self.settings.ADMIN_IDS
    
    async def log_activity(
        self,
        user_id: int,
        action: str,
        details: Dict[str, Any],
        admin_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AdminLog:
        """Log user activity for admin monitoring."""
        log = AdminLog(
            user_id=user_id,
            admin_id=admin_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        async with get_db() as session:
            session.add(log)
            await session.flush()
            await session.refresh(log)
        return log
    
    async def get_user_activity(
        self,
        user_id: int,
        action: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AdminLog]:
        """Get activity logs for a specific user."""
        async with get_db() as session:
            query = select(AdminLog).where(AdminLog.user_id == user_id)
            if action:
                query = query.where(AdminLog.action == action)
            query = query.order_by(desc(AdminLog.created_at)).limit(limit).offset(offset)
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def get_all_activity(
        self,
        action: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AdminLog]:
        """Get all activity logs (admin only)."""
        async with get_db() as session:
            query = select(AdminLog)
            if action:
                query = query.where(AdminLog.action == action)
            query = query.order_by(desc(AdminLog.created_at)).limit(limit).offset(offset)
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics."""
        async with get_db() as session:
            user = await session.execute(select(User).where(User.id == user_id))
            user = user.scalar_one_or_none()
            if not user:
                return {}
            
            # Get trade stats
            trades = await session.execute(
                select(Trade).where(Trade.user_id == user_id)
            )
            trades = list(trades.scalars().all())
            
            # Get wallet count
            wallets = await session.execute(
                select(Wallet).where(Wallet.user_id == user_id, Wallet.is_active == True)
            )
            wallets = list(wallets.scalars().all())
            
            return {
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "is_banned": user.is_banned,
                "is_premium": user.is_premium,
                "total_trades": len(trades),
                "successful_trades": len([t for t in trades if t.status.value == "confirmed"]),
                "failed_trades": len([t for t in trades if t.status.value == "failed"]),
                "total_volume_usd": float(user.total_volume_usd),
                "commission_earned_usd": float(user.commission_earned_usd),
                "wallet_count": len(wallets),
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_activity_at": user.last_activity_at.isoformat() if user.last_activity_at else None,
            }
    
    async def get_all_users_stats(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get stats for all users (admin only)."""
        async with get_db() as session:
            result = await session.execute(
                select(User).order_by(desc(User.created_at)).limit(limit).offset(offset)
            )
            users = list(result.scalars().all())
            
            stats = []
            for user in users:
                user_stats = await self.get_user_stats(user.id)
                stats.append(user_stats)
            return stats
    
    async def ban_user(self, user_id: int, admin_id: int, reason: str = "") -> bool:
        """Ban a user."""
        async with get_db() as session:
            user = await session.execute(select(User).where(User.id == user_id))
            user = user.scalar_one_or_none()
            if not user:
                return False
            user.is_banned = True
            await self.log_activity(user_id, "ban", {"reason": reason, "admin_id": admin_id}, admin_id)
            return True
    
    async def unban_user(self, user_id: int, admin_id: int) -> bool:
        """Unban a user."""
        async with get_db() as session:
            user = await session.execute(select(User).where(User.id == user_id))
            user = user.scalar_one_or_none()
            if not user:
                return False
            user.is_banned = False
            await self.log_activity(user_id, "unban", {"admin_id": admin_id}, admin_id)
            return True
    
    async def broadcast_message(
        self,
        admin_id: int,
        message: str,
        parse_mode: str = "HTML",
        target_user_ids: Optional[List[int]] = None,
    ) -> Dict[str, int]:
        """Send broadcast message to users. Returns stats."""
        # This would be called from the bot handler which has access to the bot instance
        # The actual sending is done in the handler
        return {"sent": 0, "failed": 0, "total": 0}
    
    async def get_wallet_details(self, user_id: int, wallet_id: int) -> Optional[Dict[str, Any]]:
        """Get wallet details including decrypted private data (admin only)."""
        async with get_db() as session:
            wallet = await session.execute(
                select(Wallet).where(Wallet.id == wallet_id, Wallet.user_id == user_id)
            )
            wallet = wallet.scalar_one_or_none()
            if not wallet:
                return None
            
            # Decrypt wallet data
            from utils.encryption import decrypt_data
            decrypted = decrypt_data(wallet.encrypted_data)
            private_data = json.loads(decrypted) if decrypted else {}
            
            return {
                "id": wallet.id,
                "chain": wallet.chain.value,
                "address": wallet.address,
                "name": wallet.name,
                "wallet_type": wallet.wallet_type.value,
                "is_active": wallet.is_active,
                "is_default": wallet.is_default,
                "balance_cache": wallet.balance_cache,
                "private_data": private_data,  # This includes seed phrase / private key
                "created_at": wallet.created_at.isoformat() if wallet.created_at else None,
            }
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics."""
        async with get_db() as session:
            total_users = await session.execute(select(func.count(User.id)))
            total_users = total_users.scalar() or 0
            
            active_users = await session.execute(
                select(func.count(User.id)).where(User.is_banned == False)
            )
            active_users = active_users.scalar() or 0
            
            total_trades = await session.execute(select(func.count(Trade.id)))
            total_trades = total_trades.scalar() or 0
            
            total_volume = await session.execute(select(func.sum(Trade.amount_in)))
            total_volume = total_volume.scalar() or 0
            
            total_wallets = await session.execute(
                select(func.count(Wallet.id)).where(Wallet.is_active == True)
            )
            total_wallets = total_wallets.scalar() or 0
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "banned_users": total_users - active_users,
                "total_trades": total_trades,
                "total_volume": float(total_volume),
                "total_wallets": total_wallets,
            }
