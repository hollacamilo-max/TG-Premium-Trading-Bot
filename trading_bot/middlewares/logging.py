import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from services.admin_service import AdminService

logger = logging.getLogger(__name__)
admin_service = AdminService()


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging all updates."""
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id
        
        # Log incoming update
        if isinstance(event, Message):
            logger.info(f"Message from {user_id}: {event.text[:100] if event.text else 'non-text'}")
        elif isinstance(event, CallbackQuery):
            logger.info(f"Callback from {user_id}: {event.data}")
        
        return await handler(event, data)
