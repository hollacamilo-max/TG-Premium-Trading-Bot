from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import get_settings
from database.models import User
from database.base import get_db
from services.wallet_service import WalletService
from services.referral_service import ReferralService
from services.admin_service import AdminService
from keyboards import (
    get_main_keyboard, get_settings_keyboard, 
    get_positions_keyboard, get_copy_trade_keyboard, 
    get_sniper_keyboard, get_tools_keyboard,
    get_trade_history_keyboard
)
from sqlalchemy import select
from utils.helpers import format_usd


router = Router()
settings = get_settings()
wallet_service = WalletService()
referral_service = ReferralService()
admin_service = AdminService()


class MainStates(StatesGroup):
    main_menu = State()
    settings = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, referral_code: str = None):
    """Handle /start command with optional referral code."""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    language_code = message.from_user.language_code
    is_bot = message.from_user.is_bot
    
    # Check if user is admin
    is_admin = user_id in settings.ADMIN_IDS
    
    async with get_db() as session:
        # Get or create user
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            user = User(
                id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code,
                is_bot=is_bot,
                is_admin=is_admin,
            )
            session.add(user)
            await session.flush()
            
            # Process referral if provided
            if referral_code:
                await referral_service.process_referral(user_id, referral_code)
        else:
            # Update user info
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.language_code = language_code
            user.last_activity_at = message.date
            if is_admin and not user.is_admin:
                user.is_admin = True
    
    # Log activity
    await admin_service.log_activity(
        user_id=user_id,
        action="command",
        details={"command": "start", "referral_code": referral_code},
    )
    
    # Check if user has wallets
    wallets = await wallet_service.get_user_wallets(user_id)
    has_wallets = len(wallets) > 0
    
    if has_wallets:
        wallet_text = "👛 " + str(len(wallets)) + " wallet(s) ready"
    else:
        wallet_text = "👛 No wallets imported"
    
    welcome_text = (
        "👋 Welcome to <b>Premium Trading Bot</b>, " + first_name + "!\n\n"
        "🚀 Trade on Ethereum, Base, Arbitrum, BSC, Polygon, Avalanche & Solana\n"
        "⚡ Fast swaps via Jupiter, Uniswap, 1inch & more\n"
        "🔐 Non-custodial - you control your keys\n\n"
    ) + wallet_text
    
    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard(has_wallets=has_wallets, is_admin=is_admin, is_premium=user.is_premium)
    )
    
    await state.set_state(MainStates.main_menu)


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
    """Return to main menu."""
    user_id = callback.from_user.id
    is_admin = user_id in settings.ADMIN_IDS
    
    # Get user for premium check
    async with get_db() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        is_premium = user.is_premium if user else False
    
    wallets = await wallet_service.get_user_wallets(user_id)
    has_wallets = len(wallets) > 0
    
    if has_wallets:
        wallet_text = "👛 " + str(len(wallets)) + " wallet(s) ready"
    else:
        wallet_text = "👛 No wallets imported"
    
    await callback.message.edit_text(
        "🏠 <b>Main Menu</b>\n\n" + wallet_text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard(has_wallets=has_wallets, is_admin=is_admin, is_premium=is_premium)
    )
    await callback.answer()


@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    """Show help message."""
    help_text = (
        "📖 <b>Help & Commands</b>\n\n"
        "<b>Main Commands:</b>\n"
        "/start - Start the bot\n"
        "/wallets - Manage wallets\n"
        "/trade - Open trading menu\n"
        "/portfolio - View portfolio\n"
        "/positions - View positions\n"
        "/history - Trade history\n"
        "/referral - Referral program\n"
        "/settings - Bot settings\n\n"
        "<b>Wallet Import:</b>\n"
        "• Seed phrases (12/24 words)\n"
        "• Private keys (EVM hex, Solana base58)\n"
        "• Multiple chains supported\n\n"
        "<b>Trading Features:</b>\n"
        "• Buy/Sell/Swap tokens\n"
        "• Limit orders\n"
        "• Copy trading\n"
        "• Sniper for new tokens\n"
        "• Multi-chain support\n\n"
        "<b>Admin Commands:</b>\n"
        "/admin - Admin panel (admins only)\n\n"
        "Need help? Contact support."
    )
    
    await callback.message.edit_text(
        help_text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "settings")
async def callback_settings(callback: CallbackQuery, state: FSMContext):
    """Open settings menu."""
    await callback.message.edit_text(
        "⚙️ <b>Settings</b>\n\nConfigure your trading preferences:",
        parse_mode="HTML",
        reply_markup=get_settings_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "portfolio")
async def callback_portfolio(callback: CallbackQuery):
    """Show user portfolio."""
    user_id = callback.from_user.id
    wallets = await wallet_service.get_user_wallets(user_id)
    
    if not wallets:
        await callback.message.edit_text(
            "📊 <b>Portfolio</b>\n\nNo wallets imported yet.",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
        return
    
    text = "📊 <b>Portfolio</b>\n\n"
    total_value = 0
    
    for wallet in wallets:
        chain_emoji = "🔷" if wallet.chain.value == "evm" else "🟣"
        default = " ⭐" if wallet.is_default else ""
        balance = wallet.balance_cache.get("native", "0") if wallet.balance_cache else "0"
        text += chain_emoji + " <b>" + (wallet.name or wallet.chain.value.capitalize()) + "</b>" + default + "\n"
        text += "   Address: <code>" + wallet.address[:10] + "..." + wallet.address[-6:] + "</code>\n"
        text += "   Balance: " + balance[:10] + " " + wallet.chain.value.upper() + "\n\n"
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "positions")
async def callback_positions(callback: CallbackQuery):
    """Show positions menu."""
    # In a real implementation, fetch actual positions
    await callback.message.edit_text(
        "📈 <b>Positions</b>\n\nTrack your open positions and PnL.",
        parse_mode="HTML",
        reply_markup=get_positions_keyboard(has_positions=False)
    )
    await callback.answer()


@router.callback_query(F.data == "copy_trade_menu")
async def callback_copy_trade(callback: CallbackQuery):
    """Show copy trade menu."""
    await callback.message.edit_text(
        "👥 <b>Copy Trade</b>\n\nFollow top traders and copy their trades automatically.",
        parse_mode="HTML",
        reply_markup=get_copy_trade_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "sniper_menu")
async def callback_sniper(callback: CallbackQuery):
    """Show sniper menu."""
    await callback.message.edit_text(
        "🎯 <b>Sniper</b>\n\nCatch new token launches early with automated sniping.",
        parse_mode="HTML",
        reply_markup=get_sniper_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "tools_menu")
async def callback_tools(callback: CallbackQuery):
    """Show tools menu."""
    await callback.message.edit_text(
        "🔧 <b>Tools</b>\n\nAdditional trading tools and utilities.",
        parse_mode="HTML",
        reply_markup=get_tools_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "trade_history")
async def callback_trade_history(callback: CallbackQuery):
    """Show trade history with filters."""
    from services.trading_service import TradingService
    
    user_id = callback.from_user.id
    trading_service = TradingService()
    trades = await trading_service.get_user_trades(user_id, limit=10)
    
    if not trades:
        await callback.message.edit_text(
            "📈 <b>Trade History</b>\n\nNo trades yet.",
            parse_mode="HTML",
            reply_markup=get_trade_history_keyboard()
        )
        await callback.answer()
        return
    
    text = "📈 <b>Recent Trades</b>\n\n"
    for trade in trades:
        status_emoji = "✅" if trade.status.value == "confirmed" else "❌" if trade.status.value == "failed" else "⏳"
        text += status_emoji + " " + trade.trade_type.value.upper() + " " + trade.token_in_symbol + " → " + trade.token_out_symbol + "\n"
        text += "   Amount: " + str(trade.amount_in) + " " + trade.token_in_symbol + "\n"
        text += "   Status: " + trade.status.value + "\n"
        if trade.tx_hash:
            text += "   TX: <code>" + trade.tx_hash[:10] + "..." + trade.tx_hash[-6:] + "</code>\n"
        text += "\n"
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_trade_history_keyboard()
    )
    await callback.answer()


@router.message(F.text)
async def log_all_messages(message: Message):
    """Log all user messages for admin monitoring."""
    user_id = message.from_user.id
    
    # Skip logging for admins
    if user_id in settings.ADMIN_IDS:
        return
    
    await admin_service.log_activity(
        user_id=user_id,
        action="message",
        details={"text": message.text[:500]},
    )
