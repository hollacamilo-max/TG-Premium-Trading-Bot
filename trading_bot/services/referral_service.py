@from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from config import get_settings
from utils.helpers import generate_referral_code
from database.models import User, Referral
from database.base import get_db
from sqlalchemy import select, func


class ReferralService:
    def __init__(self):
        self.settings = get_settings()
    
    async def get_or_create_referral_code(self, user_id: int) -> str:
        """Get existing referral code or create new one."""
        async with get_db() as session:
            user = await session.execute(select(User).where(User.id == user_id))
            user = user.scalar_one_or_none()
            if not user:
                raise ValueError("User not found")
            
            if user.referral_code:
                return user.referral_code
            
            # Generate unique code
            while True:
                code = generate_referral_code()
                existing = await session.execute(select(User).where(User.referral_code == code))
                if not existing.scalar_one_or_none():
                    break
            
            user.referral_code = code
            return code
    
    async def process_referral(self, new_user_id: int, referral_code: str) -> Optional[Referral]:
        """Process a referral when new user joins with a code."""
        async with get_db() as session:
            referrer = await session.execute(select(User).where(User.referral_code == referral_code))
            referrer = referrer.scalar_one_or_none()
            if not referrer or referrer.id == new_user_id:
                return None
            
            # Check if already referred
            existing = await session.execute(
                select(Referral).where(Referral.referred_id == new_user_id)
            )
            if existing.scalar_one_or_none():
                return None
            
            # Create referral record
            referral = Referral(
                referrer_id=referrer.id,
                referred_id=new_user_id,
                tier=1,
                commission_bps=self.settings.REFERRAL_COMMISSION_BPS,
            )
            session.add(referral)
            
            # Update referred user
            new_user = await session.execute(select(User).where(User.id == new_user_id))
            new_user = new_user.scalar_one_or_none()
            if new_user:
                new_user.referred_by = referrer.id
            
            await session.flush()
            await session.refresh(referral)
            return referral
    
    async def add_trade_commission(self, user_id: int, volume_usd: Decimal, fees_usd: Decimal) -> None:
        """Add commission from user trade to referrers."""
        async with get_db() as session:
            # Get direct referral (tier 1)
            referral = await session.execute(
                select(Referral).where(Referral.referred_id == user_id, Referral.tier == 1, Referral.is_active == True)
            )
            referral = referral.scalar_one_or_none()
            
            if referral:
                commission = fees_usd * Decimal(referral.commission_bps) / Decimal(10000)
                referral.total_commission_usd += commission
                referral.total_volume_usd += volume_usd
                
                # Update referrer user stats
                referrer_user = await session.execute(select(User).where(User.id == referral.referrer_id))
                referrer_user = referrer_user.scalar_one_or_none()
                if referrer_user:
                    referrer_user.commission_earned_usd += commission
                    referrer_user.total_volume_usd += volume_usd
            
            # Get tier 2 referral (referrer of referrer)
            if referral:
                tier2_referral = await session.execute(
                    select(Referral).where(Referral.referred_id == referral.referrer_id, Referral.tier == 1, Referral.is_active == True)
                )
                tier2_referral = tier2_referral.scalar_one_or_none()
                
                if tier2_referral:
                    commission = fees_usd * Decimal(self.settings.REFERRAL_TIER_2_BPS) / Decimal(10000)
                    tier2_referral.total_commission_usd += commission
                    tier2_referral.total_volume_usd += volume_usd
                    
                    tier2_referrer = await session.execute(select(User).where(User.id == tier2_referral.referrer_id))
                    tier2_referrer = tier2_referrer.scalar_one_or_none()
                    if tier2_referrer:
                        tier2_referrer.commission_earned_usd += commission
    
    async def get_referral_stats(self, user_id: int) -> dict:
        """Get referral statistics for a user."""
        async with get_db() as session:
            # Direct referrals
            direct = await session.execute(
                select(Referral).where(Referral.referrer_id == user_id, Referral.tier == 1)
            )
            direct = list(direct.scalars().all())
            
            # Indirect referrals (tier 2)
            indirect = await session.execute(
                select(Referral).where(Referral.referrer_id == user_id, Referral.tier == 2)
            )
            indirect = list(indirect.scalars().all())
            
            total_direct = len(direct)
            total_indirect = len(indirect)
            total_commission = sum(r.total_commission_usd for r in direct) + sum(r.total_commission_usd for r in indirect)
            
            return {
                "direct_referrals": total_direct,
                "indirect_referrals": total_indirect,
                "total_commission_usd": float(total_commission),
                "direct_details": [
                    {
                        "referred_id": r.referred_id,
                        "commission_usd": float(r.total_commission_usd),
                        "volume_usd": float(r.total_volume_usd),
                        "created_at": r.created_at.isoformat() if r.created_at else None,
                    }
                    for r in direct
                ],
            }
    
    async def get_referral_link(self, user_id: int, bot_username: str) -> str:
        """Generate referral link."""
        code = await self.get_or_create_referral_code(user_id)
        return f"https://t.me/{bot_username}?start={code}"
