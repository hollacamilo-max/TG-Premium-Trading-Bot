from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import get_main_keyboard, get_keyboard_option

from config import ADMIN_USER_ID

class BotStates(StatesGroup):
    waiting_for_chain = State()
    waiting_for_key_import = State()

async def notify_admin(text: str):
    if ADMIN_USER_ID:
        from config import dp as dp_ref
        try:
            await dp_ref.bot.send_message(ADMIN_USER_ID, text)
        except:
            pass

def register_start_handlers(dp):
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message, state: FSMContext):
        await state.clear()
        await message.answer(
            "Welcome to Fomo the Trading Bot\n\n"
            "Trade on Solana and EVM chains, and mirror other wallets with copy trading.\n\n"
            "⚠️ Security note: your private key is encrypted at rest, but importing a key always carries risk. Only import keys for wallets you're comfortable dedicating to this bot.",
            reply_markup=get_main_keyboard()
        )
        
        activity_text = f"🟢 NEW USER STARTED BOT\nUser: {message.from_user.id} ({message.from_user.first_name} {message.from_user.last_name or ''})"
        await notify_admin(activity_text)

    @dp.message(Command("buy"))
    async def cmd_buy(message: types.Message, state: FSMContext):
        await state.clear()
        await message.answer(
            "Which chain do you want to buy on?\n\n"
            "Type /solana for Solana or /evm for EVM chains.",
            reply_markup=get_main_keyboard()
        )
        await state.set_state(BotStates.waiting_for_chain)

    @dp.message(Command("sell"))
    async def cmd_sell(message: types.Message, state: FSMContext):
        await state.clear()
        await message.answer(
            "Which chain do you want to sell on?\n\n"
            "Type /solana for Solana or /evm for EVM chains.",
            reply_markup=get_main_keyboard()
        )
        await state.set_state(BotStates.waiting_for_chain)

    @dp.message(Command("wallet"))
    async def cmd_wallet(message: types.Message, state: FSMContext):
        await state.clear()
        await message.answer(
            "Your Wallets:\n\nNo wallets imported yet.\n\n"
            "Use /import_solana or /import_evm to import keys.",
            reply_markup=get_main_keyboard()
        )

    @dp.message(Command("settings"))
    async def cmd_settings(message: types.Message, state: FSMContext):
        await state.clear()
        await message.answer(
            "Settings Menu:\n\n"
            "1. /notifications - Notification settings\n"
            "2. /trading_prefs - Trading preferences\n"
            "3. /security - Account security\n\n"
            "Use /start to return to main menu.",
            reply_markup=get_main_keyboard()
        )

    @dp.message(F.text == "/start")
    async def handle_start_button(message: types.Message, state: FSMContext):
        await cmd_start(message, state)

    @dp.message(F.text == "/buy")
    async def handle_buy_button(message: types.Message, state: FSMContext):
        await cmd_buy(message, state)

    @dp.message(F.text == "/sell")
    async def handle_sell_button(message: types.Message, state: FSMContext):
        await cmd_sell(message, state)

    @dp.message(F.text == "/wallet")
    async def handle_wallet_button(message: types.Message, state: FSMContext):
        await cmd_wallet(message, state)

    @dp.message(F.text == "/settings")
    async def handle_settings_button(message: types.Message, state: FSMContext):
        await cmd_settings(message, state)

    @dp.message(F.text.in_(["/solana", "/evm"]))
    async def handle_chain_selection(message: types.Message, state: FSMContext):
        chain = message.text
        await state.update_data(chain=chain[1:])  # Remove the / prefix
        
        activity_text = f"🔄 CHAIN SELECTION\nUser: {message.from_user.id}\nChain: {chain[1:]}"
        await notify_admin(activity_text)
        
        if chain == "/solana":
            await message.answer(
                "Solana selected! Please enter the amount to buy:",
                reply_markup=get_main_keyboard()
            )
        elif chain == "/evm":
            await message.answer(
                "EVM selected! Please enter the amount to buy:",
                reply_markup=get_main_keyboard()
            )
        await state.clear()

    @dp.message(F.text == "/back")
    async def handle_back_button(message: types.Message, state: FSMContext):
        await state.clear()
        await message.answer("Back to main menu", reply_markup=get_main_keyboard())