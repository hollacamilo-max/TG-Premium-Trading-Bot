from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Main menu keyboard - minimal options"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="/buy")
    builder.button(text="/sell")
    builder.button(text="/wallet")
    builder.button(text="/settings")
    builder.adjust(2, 2)  # 2 buttons per row
    return builder.as_markup(resize_keyboard=True)

def get_keyboard_option() -> ReplyKeyboardMarkup:
    """Simple keyboard with back option"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="/back")
    return builder.as_markup(resize_keyboard=True)

def remove_keyboard() -> ReplyKeyboardMarkup:
    """Remove keyboard - show raw text"""
    return ReplyKeyboardRemove()

# Import all inline keyboard menus from menus.py
from keyboards.menus import (
    get_welcome_keyboard,
    get_captcha_keyboard,
    get_main_menu_keyboard,
    get_wallet_keyboard,
    get_buy_keyboard,
    get_sell_keyboard,
    get_copy_trade_keyboard,
    get_limit_orders_keyboard,
    get_auto_sell_keyboard,
    get_positions_keyboard,
    get_settings_keyboard,
    get_auto_sell_type_keyboard,
    get_connect_wallet_keyboard,
    get_confirm_keyboard,
    get_amount_keyboard,
    get_slippage_keyboard,
    get_priority_fee_keyboard,
    get_notification_keyboard,
    get_position_actions_keyboard,
    get_copy_wallet_actions_keyboard,
    get_token_info_keyboard,
    get_back_main_keyboard,
)

__all__ = [
    "get_main_keyboard",
    "get_keyboard_option",
    "remove_keyboard",
    "get_welcome_keyboard",
    "get_captcha_keyboard",
    "get_main_menu_keyboard",
    "get_wallet_keyboard",
    "get_buy_keyboard",
    "get_sell_keyboard",
    "get_copy_trade_keyboard",
    "get_limit_orders_keyboard",
    "get_auto_sell_keyboard",
    "get_positions_keyboard",
    "get_settings_keyboard",
    "get_auto_sell_type_keyboard",
    "get_connect_wallet_keyboard",
    "get_confirm_keyboard",
    "get_amount_keyboard",
    "get_slippage_keyboard",
    "get_priority_fee_keyboard",
    "get_notification_keyboard",
    "get_position_actions_keyboard",
    "get_copy_wallet_actions_keyboard",
    "get_token_info_keyboard",
    "get_back_main_keyboard",
]
