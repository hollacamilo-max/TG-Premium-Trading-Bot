import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from config import get_settings
from database.base import init_db, close_db
from handlers import main_router, wallet_router, trading_router, admin_router, referral_router
from middlewares import AuthMiddleware, ReferralMiddleware, LoggingMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting bot...")
    init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down bot...")
    await close_db()
    logger.info("Database closed")


async def main():
    """Main bot entry point."""
    # Initialize bot
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    # Choose storage
    if settings.REDIS_URL:
        storage = RedisStorage.from_url(settings.REDIS_URL)
        logger.info("Using Redis storage")
    else:
        storage = MemoryStorage()
        logger.info("Using Memory storage")
    
    # Create dispatcher
    dp = Dispatcher(storage=storage)
    
    # Register middlewares
    dp.update.middleware(LoggingMiddleware())
    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(ReferralMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    # Register routers
    dp.include_router(main_router)
    dp.include_router(wallet_router)
    dp.include_router(trading_router)
    dp.include_router(admin_router)
    dp.include_router(referral_router)
    
    # Start polling
    logger.info("Bot started successfully!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise
