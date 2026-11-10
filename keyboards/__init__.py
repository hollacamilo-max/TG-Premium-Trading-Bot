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