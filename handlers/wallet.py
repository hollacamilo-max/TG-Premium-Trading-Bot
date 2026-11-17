 from aiogram import types, F
 from aiogram.filters import Command
 from aiogram.fsm.context import FSMContext
 from aiogram.fsm.state import State, StatesGroup
 
 from keyboards import get_main_keyboard, get_keyboard_option
 
 from config import get_settings
 
 settings = get_settings()
 
 class WalletStates(StatesGroup):
     waiting_for_solana_key = State()
     waiting_for_evm_key = State()
 
 async def notify_admin(bot, text: str):
     if settings.ADMIN_IDS:
         try:
             await bot.send_message(settings.ADMIN_IDS[0], text)
         except:
             pass
 
 def register_wallet_handlers(dp):
     # Old wallet import handlers removed - now handled in start.py with proper validation
     # This file is kept for backward compatibility with /import_solana and /import_evm commands
     
     @dp.message(Command("import_solana"))
     async def import_solana_cmd(message: types.Message, state: FSMContext):
         await message.answer(
             "Please use the 'Connect Wallet' menu to import your wallet with proper validation.",
             reply_markup=get_main_keyboard()
         )
 
     @dp.message(Command("import_evm"))
     async def import_evm_cmd(message: types.Message, state: FSMContext):
         await message.answer(
             "Please use the 'Connect Wallet' menu to import your wallet with proper validation.",
             reply_markup=get_main_keyboard()
         )
 
     @dp.message(F.text == "/import_solana")
     async def import_solana_handler(message: types.Message, state: FSMContext):
         await import_solana_cmd(message, state)
 
     @dp.message(F.text == "/import_evm")
     async def import_evm_handler(message: types.Message, state: FSMContext):
         await import_evm_cmd(message, state)
