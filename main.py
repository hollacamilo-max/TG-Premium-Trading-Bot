import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN, ADMIN_USER_ID
from handlers.start import register_start_handlers
from handlers.buy import register_buy_handlers
from handlers.sell import register_sell_handlers
from handlers.wallet import register_wallet_handlers
from handlers.settings import register_settings_handlers

# Create dispatcher
dp = Dispatcher()

async def main():
    bot = Bot(token=BOT_TOKEN)
    
    # Register all feature handlers
    register_start_handlers(dp)
    register_buy_handlers(dp)
    register_sell_handlers(dp)
    register_wallet_handlers(dp)
    register_settings_handlers(dp)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")