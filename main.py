import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

settings = get_settings()


async def main():
    # Initialize bot
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    # Choose storage
    if settings.REDIS_URL:
        storage = RedisStorage.from_url(settings.REDIS_URL)
        logger.info('Using Redis storage')
    else:
        storage = MemoryStorage()
        logger.info('Using Memory storage')
    
    # Create dispatcher
    dp = Dispatcher(storage=storage)
    
    # Import handlers after settings is loaded
    from handlers.start import register_start_handlers
    from handlers.buy import register_buy_handlers
    from handlers.sell import register_sell_handlers
    from handlers.wallet import register_wallet_handlers
    from handlers.settings import register_settings_handlers
    from handlers.menu_callbacks import register_menu_callbacks
    
    # Register all feature handlers
    register_start_handlers(dp)
    register_buy_handlers(dp)
    register_sell_handlers(dp)
    register_wallet_handlers(dp)
    register_settings_handlers(dp)
    register_menu_callbacks(dp)
    
    # Start polling
    logger.info('Bot started successfully!')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Bot stopped by user')
    except Exception as e:
        logger.error(f'Bot crashed: {e}')
        raise
