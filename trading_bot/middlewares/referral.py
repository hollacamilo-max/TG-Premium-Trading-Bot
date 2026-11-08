from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from services.referral_service import ReferralService

referral_service = ReferralService()


class ReferralMiddleware(BaseMiddleware):
    """Middleware to extract referral code from /start command."""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        # Extract referral code from /start payload
        referral_code = None
        if event.text and event.text.startswith("/start"):
            parts = event.text.split()
            if len(parts) > 1:
                referral_code = parts[1]
        
        data["referral_code"] = referral_code
        return await handler(event, data)
