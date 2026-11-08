from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import get_settings
from services.wallet_service import WalletService
from services.trading_service import TradingService
from services.admin_service import AdminService
from keyboards import get_trading_keyboard, get_slippage_keyboard, get_amount_keyboard, get_dex_select_keyboard, get_confirm_trade_keyboard
from database.models import TradeType, ChainType

router = Router()
settings = get_settings()
wallet_service = WalletService()
trading_service = TradingService()
admin_service = AdminService()


class TradingStates(StatesGroup):
    selecting_wallet = State()
    selecting_action = State()
    selecting_token = State()
    entering_amount = State()
    confirming = State()


@router.callback_query(F.data == "trade_menu")
async def callback_trade_menu(callback: CallbackQuery, state: FSMContext):
    """Show trading menu - select wallet first."""
    user_id = callback.from_user.id
    wallets = await wallet_service.get_user_wallets(user_id)
    
    if not wallets:
        await callback.message.edit_text(
            "💰 <b>Trade</b>\n\nNo wallets imported. Please import a wallet first.",
            parse_mode="HTML",
            reply_markup=None
        )
        await callback.answer()
        return
    
    # Show wallet selection for trading
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    builder = InlineKeyboardBuilder()
    for wallet in wallets:
        chain_emoji = "🔷" if wallet.chain == ChainType.EVM else "🟣"
        default = " ⭐" if wallet.is_default else ""
        builder.row(InlineKeyboardButton(
            text=chain_emoji + " " + (wallet.name or wallet.chain.value.capitalize()) + default,
            callback_data="trade_wallet_" + str(wallet.id)
        ))
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="main_menu"))
    
    await callback.message.edit_text(
        "💰 <b>Trade</b>\n\nSelect a wallet to trade with:",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("trade_wallet_"))
async def callback_trade_wallet(callback: CallbackQuery, state: FSMContext):
    """Open trading menu for selected wallet."""
    wallet_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    wallet = await wallet_service.get_wallet(wallet_id, user_id)
    if not wallet:
        await callback.answer("Wallet not found", show_alert=True)
        return
    
    await state.update_data(wallet_id=wallet_id, chain=wallet.chain.value)
    
    chain_emoji = "🔷" if wallet.chain == ChainType.EVM else "🟣"
    
    await callback.message.edit_text(
        chain_emoji + " <b>Trading - " + (wallet.name or wallet.chain.value.capitalize()) + "</b>\n\n"
        "Select action:",
        parse_mode="HTML",
        reply_markup=get_trading_keyboard(wallet.chain.value, wallet_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("trade_buy_"))
async def callback_trade_buy(callback: CallbackQuery, state: FSMContext):
    """Handle buy action."""
    wallet_id = int(callback.data.split("_")[2])
    await state.update_data(trade_type="buy", wallet_id=wallet_id)
    
    wallet = await wallet_service.get_wallet(wallet_id, callback.from_user.id)
    chain = wallet.chain.value if wallet else "ethereum"
    
    await callback.message.edit_text(
        "🟢 <b>Buy Tokens</b>\n\n"
        "Select DEX:",
        parse_mode="HTML",
        reply_markup=get_dex_select_keyboard(wallet_id, chain)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("trade_sell_"))
async def callback_trade_sell(callback: CallbackQuery, state: FSMContext):
    """Handle sell action."""
    wallet_id = int(callback.data.split("_")[2])
    await state.update_data(trade_type="sell", wallet_id=wallet_id)
    
    wallet = await wallet_service.get_wallet(wallet_id, callback.from_user.id)
    chain = wallet.chain.value if wallet else "ethereum"
    
    await callback.message.edit_text(
        "🔴 <b>Sell Tokens</b>\n\n"
        "Select DEX:",
        parse_mode="HTML",
        reply_markup=get_dex_select_keyboard(wallet_id, chain)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("trade_swap_"))
async def callback_trade_swap(callback: CallbackQuery, state: FSMContext):
    """Handle swap action."""
    wallet_id = int(callback.data.split("_")[2])
    await state.update_data(trade_type="swap", wallet_id=wallet_id)
    
    wallet = await wallet_service.get_wallet(wallet_id, callback.from_user.id)
    chain = wallet.chain.value if wallet else "ethereum"
    
    await callback.message.edit_text(
        "🔄 <b>Swap Tokens</b>\n\n"
        "Select DEX:",
        parse_mode="HTML",
        reply_markup=get_dex_select_keyboard(wallet_id, chain)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("trade_slippage_"))
async def callback_trade_slippage(callback: CallbackQuery, state: FSMContext):
    """Show slippage settings."""
    wallet_id = int(callback.data.split("_")[2])
    data = await state.get_data()
    current_slippage = data.get("slippage", settings.DEFAULT_SLIPPAGE)
    
    await callback.message.edit_text(
        "🎯 <b>Slippage Tolerance</b>\n\n"
        "Current: " + str(current_slippage) + "%\n\n"
        "Select new slippage:",
        parse_mode="HTML",
        reply_markup=get_slippage_keyboard(current_slippage, wallet_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_slippage_"))
async def callback_set_slippage(callback: CallbackQuery, state: FSMContext):
    """Set slippage value."""
    parts = callback.data.split("_")
    slippage = float(parts[2])
    wallet_id = int(parts[3])
    
    await state.update_data(slippage=slippage)
    
    await callback.answer("✅ Slippage set to " + str(slippage) + "%", show_alert=True)
    
    # Go back to trading menu
    await callback_trade_wallet(callback, state)


@router.callback_query(F.data.startswith("slippage_custom_"))
async def callback_slippage_custom(callback: CallbackQuery, state: FSMContext):
    """Custom slippage input."""
    wallet_id = int(callback.data.split("_")[2])
    await state.update_data(wallet_id=wallet_id, waiting_custom_slippage=True)
    
    await callback.message.edit_text(
        "✏️ <b>Custom Slippage</b>\n\n"
        "Enter slippage percentage (0.1 - 50):",
        parse_mode="HTML",
        reply_markup=None
    )
    await callback.answer()


@router.message(F.text, lambda m: (m.bot.get("state").get("waiting_custom_slippage") if m.bot.get("state") else False))
async def process_custom_slippage(message: Message, state: FSMContext):
    """Process custom slippage input."""
    try:
        slippage = float(message.text.strip())
        if slippage < 0.1 or slippage > 50:
            raise ValueError()
    except ValueError:
        await message.answer("❌ Invalid slippage. Enter a number between 0.1 and 50.")
        return
    
    await state.update_data(slippage=slippage, waiting_custom_slippage=False)
    await message.answer("✅ Slippage set to " + str(slippage) + "%")
    
    # Go back to trading menu
    data = await state.get_data()
    wallet_id = data.get("wallet_id")
    if wallet_id:
        from aiogram.types import CallbackQuery
        # Simulate callback
        await callback_trade_wallet(message, state)


@router.callback_query(F.data.startswith("trade_menu_"))
async def callback_trade_menu_back(callback: CallbackQuery, state: FSMContext):
    """Back to trading menu."""
    wallet_id = int(callback.data.split("_")[2])
    await callback_trade_wallet(callback, state)


# Placeholder for actual trading execution
@router.callback_query(F.data.startswith("confirm_"))
async def callback_confirm_trade(callback: CallbackQuery, state: FSMContext):
    """Confirm and execute trade."""
    await callback.answer("⚠️ Trade execution not fully implemented yet. This is a template.", show_alert=True)
