from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import re

from keyboards import (
    get_wallet_keyboard, get_buy_keyboard, get_sell_keyboard,
    get_copy_trade_keyboard, get_limit_orders_keyboard,
    get_auto_sell_keyboard, get_positions_keyboard, get_settings_keyboard,
    get_auto_sell_type_keyboard, get_connect_wallet_keyboard,
    get_slippage_keyboard, get_priority_fee_keyboard,
    get_notification_keyboard, get_amount_keyboard,
    get_confirm_keyboard, get_back_main_keyboard,
    get_token_info_keyboard, get_position_actions_keyboard,
    get_copy_wallet_actions_keyboard,
)
from config import get_settings
from utils.admin_notify import notify_admin, format_activity
from services import token_service

settings = get_settings()


def register_menu_callbacks(dp):
    """Register all menu callback handlers."""

    @dp.callback_query(F.data == "wallet_withdraw")
    async def callback_wallet_withdraw(callback: types.CallbackQuery, state: FSMContext):
        await state.update_data(action="withdraw")
        await callback.message.edit_text(
            "📤 <b>Withdraw SOL</b>\n\n"
            "Select amount to withdraw:",
            parse_mode="HTML",
            reply_markup=get_amount_keyboard("withdraw")
        )
        await callback.answer()

    @dp.callback_query(F.data == "wallet_refresh")
    async def callback_wallet_refresh(callback: types.CallbackQuery, state: FSMContext):
        await callback.answer("Balance refreshed!")
        await callback.message.edit_text(
            "👛 <b>Wallet Menu</b>\n\nManage your wallets:",
            parse_mode="HTML",
            reply_markup=get_wallet_keyboard(has_wallet=True, balance="0.00 SOL")
        )
        await callback.answer()

    @dp.callback_query(F.data == "wallet_history")
    async def callback_wallet_history(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "📜 <b>Transaction History</b>\n\n"
            "No transactions yet.\n\n"
            "Your transaction history will appear here.",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    # ==================== BUY MENU CALLBACKS ====================

    @dp.callback_query(F.data == "buy_by_address")
    async def callback_buy_by_address(callback: types.CallbackQuery, state: FSMContext):
        """Prompt user to enter token contract address for buying."""
        await state.set_state(BuySellStates.waiting_for_token_address)
        await state.update_data(buy_method="by_address")
        await callback.message.edit_text(
            "🎯 <b>Buy by Token Address</b>\n\n"
            "Please send the token contract address.\n\n"
            "The bot will automatically detect the chain (Solana or EVM).",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()


    @dp.callback_query(F.data == "buy_search")
    async def callback_buy_search(callback: types.CallbackQuery, state: FSMContext):
        """Prompt user to search for a token by name/symbol."""
        await state.set_state(BuySellStates.waiting_for_token_search)
        await state.update_data(buy_method="search")
        await callback.message.edit_text(
            "🔍 <b>Search Token</b>\n\n"
            "Enter the token name or symbol to search.\n\n"
            "Examples:\n"
            "• <code>SOL</code> or <code>Solana</code>\n"
            "• <code>USDC</code> or <code>USD Coin</code>\n"
            "• <code>BONK</code> or <code>Bonk</code>\n\n"
            "The bot will search on the selected chain.",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()


    @dp.callback_query(F.data == "buy_trending")
    async def callback_buy_trending(callback: types.CallbackQuery, state: FSMContext):
        """Show trending tokens for buying."""
        data = await state.get_data()
        chain = data.get("chain", "solana")
        
        await callback.message.edit_text(
            f"💎 <b>Trending Tokens ({chain.capitalize()})</b>\n\n"
            "Fetching trending tokens...",
            parse_mode="HTML"
        )
        
        try:
            trending = await token_service.get_trending(chain, limit=10)
            
            if not trending:
                await callback.message.edit_text(
                    f"💎 <b>Trending Tokens ({chain.capitalize()})</b>\n\n"
                    "No trending data available at the moment.\n"
                    "Please try again later.",
                    parse_mode="HTML",
                    reply_markup=get_back_main_keyboard()
                )
                await callback.answer()
                return
            
            text = f"💎 <b>Trending Tokens ({chain.capitalize()})</b>\n\n"
            for i, token in enumerate(trending, 1):
                price = token.get('price_usd', 'N/A')
                change = token.get('price_change_24h', 'N/A')
                vol = token.get('volume_24h', 0)
                text += f"{i}. <b>{token.get('symbol', 'UNK')}</b> ({token.get('name', 'Unknown')})\n"
                text += f"   💰 ${price} | 📈 {change}% | 📊 Vol: ${vol:,.0f}\n"
                text += f"   📍 <code>{token.get('address', '')[:12]}...{token.get('address', '')[-8:]}</code>\n\n"
            
            # Create keyboard with trending tokens
            from aiogram.utils.keyboard import InlineKeyboardBuilder
            from aiogram.types import InlineKeyboardButton
            builder = InlineKeyboardBuilder()
            for token in trending[:8]:
                builder.row(InlineKeyboardButton(
                    text=f"💎 {token.get('symbol', 'UNK')} - ${token.get('price_usd', 'N/A')}",
                    callback_data=f"buy_token_{token.get('address')}_{chain}"
                ))
            builder.row(InlineKeyboardButton(text="🔙 Back to Buy Menu", callback_data="menu_buy"))
            
            await callback.message.edit_text(
                text,
                parse_mode="HTML",
                reply_markup=builder.as_markup()
            )
        except Exception as e:
            print(f"Error fetching trending: {e}")
            await callback.message.edit_text(
                "❌ Error fetching trending tokens. Please try again.",
                parse_mode="HTML",
                reply_markup=get_back_main_keyboard()
            )
        await callback.answer()


    @dp.callback_query(F.data == "buy_favorites")
    async def callback_buy_favorites(callback: types.CallbackQuery, state: FSMContext):
        """Show user's favorite tokens."""
        # TODO: Implement favorites from database
        await callback.message.edit_text(
            "⭐ <b>Favorite Tokens</b>\n\n"
            "No favorite tokens saved yet.\n\n"
            "Add tokens to favorites from the token info screen.",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()


    @dp.callback_query(F.data.startswith("buy_token_"))
    async def callback_buy_token(callback: types.CallbackQuery, state: FSMContext):
        """Handle buying a specific token from trending/search results."""
        parts = callback.data.split("_")
        if len(parts) >= 4:
            token_address = parts[2]
            chain = parts[3]
            
            await callback.message.edit_text(
                f"🔍 <b>Fetching Token Info</b>\n\n"
                f"Chain: {chain.capitalize()}\n"
                f"Address: <code>{token_address}</code>\n\n"
                "Please wait...",
                parse_mode="HTML"
            )
            
            token_info = await token_service.get_token_info_auto(token_address)
            
            if token_info:
                price = token_info.get('price_usd', 'N/A')
                change = token_info.get('price_change_24h', 'N/A')
                name = token_info.get('name', 'Unknown')
                symbol = token_info.get('symbol', 'UNK')
                
                await callback.message.edit_text(
                    f"💎 <b>{name} ({symbol})</b>\n\n"
                    f"📍 Address: <code>{token_address}</code>\n"
                    f"💰 Price: ${price}\n"
                    f"📈 24h Change: {change}%\n"
                    f"🔗 Chain: {chain.capitalize()}\n\n"
                    "What would you like to do?",
                    parse_mode="HTML",
                    reply_markup=get_token_info_keyboard(token_address)
                )
            else:
                await callback.message.edit_text(
                    "❌ Could not fetch token information.\n"
                    "Please verify the address is correct.",
                    parse_mode="HTML",
                    reply_markup=get_back_main_keyboard()
                )
        await callback.answer()


    # ==================== SELL MENU CALLBACKS ====================

    @dp.callback_query(F.data == "sell_by_address")
    async def callback_sell_by_address(callback: types.CallbackQuery, state: FSMContext):
        """Prompt user to enter token contract address for selling."""
        await state.set_state(BuySellStates.waiting_for_sell_token_address)
        await state.update_data(sell_method="by_address")
        await callback.message.edit_text(
            "🎯 <b>Sell by Token Address</b>\n\n"
            "Please send the token contract address you want to sell.\n\n"
            "The bot will automatically detect the chain (Solana or EVM).",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()


    @dp.callback_query(F.data == "sell_positions")
    async def callback_sell_positions(callback: types.CallbackQuery, state: FSMContext):
        """Show user's positions for selling."""
        # TODO: Fetch actual positions from database
        await callback.message.edit_text(
            "💼 <b>Your Positions</b>\n\n"
            "No open positions found.\n\n"
            "Buy some tokens first to see them here.",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()


    # ==================== STATES FOR BUY/SELL ====================

    class BuySellStates(StatesGroup):
        waiting_for_token_address = State()
        waiting_for_token_search = State()
        waiting_for_sell_token_address = State()


    # ==================== HANDLE TEXT INPUT FOR BUY/SELL ====================

    @dp.message(BuySellStates.waiting_for_token_address)
    async def handle_buy_token_address(message: types.Message, state: FSMContext):
        """Handle token address input for buying."""
        import logging
        logger = logging.getLogger(__name__)

        text = message.text.strip()
        data = await state.get_data()
        chain = data.get("chain", "solana")

        logger.info(f"User {message.from_user.id} entered token address: {text}")

        # Detect chain from address format
        solana_pattern = r"^[1-9A-HJ-NP-Za-km-z]{32,44}$"
        evm_pattern = r"^0x[a-fA-F0-9]{40}$"

        is_solana = bool(re.match(solana_pattern, text))
        is_evm = bool(re.match(evm_pattern, text))

        if is_solana:
            detected_chain = "solana"
        elif is_evm:
            detected_chain = chain if chain != "solana" else "ethereum"
        else:
            await message.answer(
                "❌ Invalid address format.\n\n"
                "Please enter a valid:\n"
                "• Solana address (Base58, 32-44 chars)\n"
                "• EVM address (0x... 42 chars)",
                parse_mode="HTML",
                reply_markup=get_back_main_keyboard()
            )
            return

        await message.answer(
            f"🔍 <b>Fetching Token Info</b>\n\n"
            f"Chain: {detected_chain.capitalize()}\n"
            f"Address: <code>{text}</code>\n\n"
            "Please wait...",
            parse_mode="HTML"
        )

        try:
            token_info = await token_service.get_token_info_auto(text)
            logger.info(f"Token info result for {text}: {token_info is not None}")
        except Exception as e:
            logger.error(f"Error fetching token info for {text}: {e}", exc_info=True)
            await message.answer(
                f"❌ Error fetching token info: {type(e).__name__}"
                "Please try again later.",
                parse_mode="HTML",
                reply_markup=get_back_main_keyboard()
            )
            await state.clear()
            return

        if token_info:
            price = token_info.get("price_usd", "N/A")
            change = token_info.get("price_change_24h", "N/A")
            name = token_info.get("name", "Unknown")
            symbol = token_info.get("symbol", "UNK")

            await message.answer(
                f"💎 <b>{name} ({symbol})</b>\n\n"
                f"📍 Address: <code>{text}</code>\n"
                f"💰 Price: ${price}\n"
                f"📈 24h Change: {change}%\n"
                f"🔗 Chain: {detected_chain.capitalize()}\n\n"
                "What would you like to do?",
                parse_mode="HTML",
                reply_markup=get_token_info_keyboard(text)
            )
        else:
            await message.answer(
                "❌ Could not fetch token information.\n"
                "This token may not have trading pairs on DexScreener yet.\n"
                "Please verify the address is correct.",
                parse_mode="HTML",
                reply_markup=get_back_main_keyboard()
            )

        await state.clear()


    @dp.message(BuySellStates.waiting_for_token_search)
    async def handle_buy_token_search(message: types.Message, state: FSMContext):
        """Handle token search input for buying."""
        query = message.text.strip()
        data = await state.get_data()
        chain = data.get("chain", "solana")
        
        if len(query) < 2:
            await message.answer(
                "❌ Search query too short. Enter at least 2 characters.",
                parse_mode="HTML",
                reply_markup=get_back_main_keyboard()
            )
            return
        
        await message.answer(
            f"🔍 <b>Searching for '{query}' on {chain.capitalize()}</b>\n\n"
            "Please wait...",
            parse_mode="HTML"
        )
        
        results = await token_service.search_tokens(query, chain)
        
        if not results:
            await message.answer(
                f"❌ No tokens found for '{query}' on {chain.capitalize()}.\n"
                "Try a different search term.",
                parse_mode="HTML",
                reply_markup=get_back_main_keyboard()
            )
            await state.clear()
            return
        
        text = f"🔍 <b>Search Results for '{query}' ({chain.capitalize()})</b>\n\n"
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        
        for i, token in enumerate(results[:10], 1):
            price = token.get('price_usd', 'N/A')
            text += f"{i}. <b>{token.get('symbol', 'UNK')}</b> ({token.get('name', 'Unknown')})\n"
            if price != 'N/A':
                text += f"   💰 ${price}\n"
            text += f"   📍 <code>{token.get('address', '')[:12]}...{token.get('address', '')[-8:]}</code>\n\n"
            
            builder.row(InlineKeyboardButton(
                text=f"💎 {token.get('symbol', 'UNK')} - ${price}",
                callback_data=f"buy_token_{token.get('address')}_{chain}"
            ))
    
        builder.row(InlineKeyboardButton(text="🔙 Back to Buy Menu", callback_data="menu_buy"))
        
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=builder.as_markup()
        )
        await state.clear()


    @dp.message(BuySellStates.waiting_for_sell_token_address)
    async def handle_sell_token_address(message: types.Message, state: FSMContext):
        """Handle token address input for selling."""
        text = message.text.strip()
        data = await state.get_data()
        chain = data.get("chain", "solana")
        
        # Detect chain from address format
        solana_pattern = r'^[1-9A-HJ-NP-Za-km-z]{32,44}$'
        evm_pattern = r'^0x[a-fA-F0-9]{40}$'
        
        is_solana = bool(re.match(solana_pattern, text))
        is_evm = bool(re.match(evm_pattern, text))
        
        if is_solana:
            detected_chain = "solana"
        elif is_evm:
            detected_chain = chain if chain != "solana" else "ethereum"
        else:
            await message.answer(
                "❌ Invalid address format.\n\n"
                "Please enter a valid:\n"
                "• Solana address (Base58, 32-44 chars)\n"
                "• EVM address (0x... 42 chars)",
                parse_mode="HTML",
                reply_markup=get_back_main_keyboard()
            )
            return
        
        await message.answer(
            f"🔍 <b>Fetching Token Info</b>\n\n"
            f"Chain: {detected_chain.capitalize()}\n"
            f"Address: <code>{text}</code>\n\n"
            "Please wait...",
            parse_mode="HTML"
        )
        
        try:
            token_info = await token_service.get_token_info_auto(text)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching token info for {text}: {e}", exc_info=True)
            await message.answer(
                f"Error fetching token info: {type(e).__name__}"
                "Please try again later.",
                parse_mode="HTML",
                reply_markup=get_back_main_keyboard()
            )
            await state.clear()
            return

        if token_info:
            price = token_info.get('price_usd', 'N/A')
            change = token_info.get('price_change_24h', 'N/A')
            name = token_info.get('name', 'Unknown')
            symbol = token_info.get('symbol', 'UNK')
            
            await message.answer(
                f"💎 <b>{name} ({symbol})</b>\n\n"
                f"📍 Address: <code>{text}</code>\n"
                f"💰 Price: ${price}\n"
                f"📈 24h Change: {change}%\n"
                f"🔗 Chain: {detected_chain.capitalize()}\n\n"
                "What would you like to do?",
                parse_mode="HTML",
                reply_markup=get_token_info_keyboard(text)
            )
        else:
            await message.answer(
                "❌ Could not fetch token information.\n"
                "Please verify the address is correct.",
                parse_mode="HTML",
                reply_markup=get_back_main_keyboard()
            )
        
        await state.clear()

    print("All menu callbacks registered!")
