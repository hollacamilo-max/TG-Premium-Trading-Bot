from aiogram import types, F
from aiogram.fsm.context import FSMContext
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

    print("✅ All menu callbacks registered!")
