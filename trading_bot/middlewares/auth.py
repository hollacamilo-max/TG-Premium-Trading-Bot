from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from config import get_settings
from database.models import User
from database.base import get_db
from sqlalchemy import select

settings = get_settings()


class AuthMiddleware(BaseMiddleware):
    """Middleware to attach user object to handler data."""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id
        
        # Get or create user
        async with get_db() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if not user:
                user = User(
                    id=user_id,
                    username=event.from_user.username,
                    first_name=event.from_user.first_name,
                    last_name=event.from_user.last_name,
                    language_code=event.from_user.language_code,
                    is_bot=event.from_user.is_bot,
                    is_admin=user_id in settings.ADMIN_IDS,
                )
                session.add(user)
                await session.flush()
            else:
                # Update last activity
                user.last_activity_at = event.date if hasattr(event, "date") else None
            
            data["user"] = user
        
        return await handler(event, data)
