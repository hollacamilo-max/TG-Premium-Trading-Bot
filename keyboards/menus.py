from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Tuple, Optional


def get_welcome_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Tap /start to enjoy", callback_data="start_bot")
    return builder.as_markup()


def get_captcha_keyboard(captcha_code: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    row = []
    for i, char in enumerate(captcha_code):
        row.append(InlineKeyboardButton(text=char, callback_data=f"captcha_{char}"))
        if len(row) == 3:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)
    builder.row(InlineKeyboardButton(text="🔄 Refresh", callback_data="captcha_refresh"))
    builder.row(InlineKeyboardButton(text="✅ Verify", callback_data="captcha_verify"))
    return builder.as_markup()


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔗 Connect Wallet", callback_data="menu_connect_wallet"),
        InlineKeyboardButton(text="👛 Wallet", callback_data="menu_wallet")
    )
    builder.row(
        InlineKeyboardButton(text="🟢 Buy", callback_data="menu_buy"),
        InlineKeyboardButton(text="🔴 Sell", callback_data="menu_sell")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Copy Trade", callback_data="menu_copy_trade"),
        InlineKeyboardButton(text="📊 Limit Orders", callback_data="menu_limit_orders")
    )
    builder.row(
        InlineKeyboardButton(text="⚡ Auto Sell", callback_data="menu_auto_sell"),
        InlineKeyboardButton(text="💼 Positions", callback_data="menu_positions")
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ Settings", callback_data="menu_settings")
    )
    return builder.as_markup()


def get_wallet_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💰 Deposit SOL", callback_data="wallet_deposit"),
        InlineKeyboardButton(text="📤 Withdraw", callback_data="wallet_withdraw")
    )
    builder.row(
        InlineKeyboardButton(text="🔑 Import Wallet", callback_data="wallet_import"),
        InlineKeyboardButton(text="🔄 Refresh Balance", callback_data="wallet_refresh")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Transaction History", callback_data="wallet_history"),
        InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_main")
    )
    return builder.as_markup()


def get_buy_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎯 By Token Address", callback_data="buy_by_address"),
        InlineKeyboardButton(text="🔍 Search Token", callback_data="buy_search")
    )
    builder.row(
        InlineKeyboardButton(text="💎 Trending", callback_data="buy_trending"),
        InlineKeyboardButton(text="⭐ Favorites", callback_data="buy_favorites")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_main")
    )
    return builder.as_markup()


def get_sell_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💼 Sell from Positions", callback_data="sell_positions"),
        InlineKeyboardButton(text="🎯 Sell by Token Address", callback_data="sell_by_address")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_main")
    )
    return builder.as_markup()


def get_copy_trade_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Add Wallet to Copy", callback_data="copy_add_wallet"),
        InlineKeyboardButton(text="📋 My Copy Wallets", callback_data="copy_list_wallets")
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ Copy Trade Settings", callback_data="copy_settings"),
        InlineKeyboardButton(text="📊 Copy Trade History", callback_data="copy_history")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_main")
    )
    return builder.as_markup()


def get_limit_orders_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Create Limit Order", callback_data="limit_create"),
        InlineKeyboardButton(text="📋 My Limit Orders", callback_data="limit_list")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_main")
    )
    return builder.as_markup()


def get_auto_sell_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Add Auto Sell Rule", callback_data="autosell_add"),
        InlineKeyboardButton(text="📋 My Auto Sell Rules", callback_data="autosell_list")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_main")
    )
    return builder.as_markup()


def get_positions_keyboard(has_positions: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if has_positions:
        builder.row(InlineKeyboardButton(text="🔄 Refresh Prices", callback_data="positions_refresh"))
    builder.row(InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_main"))
    return builder.as_markup()


def get_settings_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎯 Slippage", callback_data="settings_slippage"),
        InlineKeyboardButton(text="⚡ Priority Fee", callback_data="settings_priority_fee")
    )
    builder.row(
        InlineKeyboardButton(text="🔔 Notifications", callback_data="settings_notifications"),
        InlineKeyboardButton(text="🌐 Language", callback_data="settings_language")
    )
    builder.row(
        InlineKeyboardButton(text="🔒 Security", callback_data="settings_security"),
        InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_main")
    )
    return builder.as_markup()


def get_auto_sell_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🟢 Target", callback_data="autosell_type_target"),
        InlineKeyboardButton(text="🟢 Stop Loss", callback_data="autosell_type_stop"),
    )
    builder.row(
        InlineKeyboardButton(text="🟢 Take Profit", callback_data="autosell_type_take"),
        InlineKeyboardButton(text="🔙 Back", callback_data="menu_auto_sell"),
    )
    return builder.as_markup()


def get_connect_wallet_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📱 Phantom", callback_data="connect_phantom"),
        InlineKeyboardButton(text="🦊 Solflare", callback_data="connect_solflare")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_main")
    )
    return builder.as_markup()


def get_confirm_keyboard(action: str, confirm_data: str, cancel_data: str = "back_main") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Confirm", callback_data=confirm_data),
        InlineKeyboardButton(text="❌ Cancel", callback_data=cancel_data)
    )
    return builder.as_markup()


def get_amount_keyboard(action: str, amounts: List[float] = None) -> InlineKeyboardMarkup:
    if amounts is None:
        amounts = [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
    
    builder = InlineKeyboardBuilder()
    row = []
    for amount in amounts:
        row.append(InlineKeyboardButton(text=f"{amount} SOL", callback_data=f"{action}_amount_{amount}"))
        if len(row) == 3:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)
    
    builder.row(
        InlineKeyboardButton(text="✏️ Custom Amount", callback_data=f"{action}_custom"),
        InlineKeyboardButton(text="🔙 Back", callback_data="back_main")
    )
    return builder.as_markup()


def get_slippage_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="0.5%", callback_data="slippage_0.5"),
        InlineKeyboardButton(text="1%", callback_data="slippage_1"),
        InlineKeyboardButton(text="2%", callback_data="slippage_2")
    )
    builder.row(
        InlineKeyboardButton(text="3%", callback_data="slippage_3"),
        InlineKeyboardButton(text="5%", callback_data="slippage_5"),
        InlineKeyboardButton(text="10%", callback_data="slippage_10")
    )
    builder.row(
        InlineKeyboardButton(text="✏️ Custom", callback_data="slippage_custom"),
        InlineKeyboardButton(text="🔙 Back", callback_data="menu_settings")
    )
    return builder.as_markup()


def get_priority_fee_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="0.0001 SOL", callback_data="priority_0.0001"),
        InlineKeyboardButton(text="0.0005 SOL", callback_data="priority_0.0005"),
        InlineKeyboardButton(text="0.001 SOL", callback_data="priority_0.001")
    )
    builder.row(
        InlineKeyboardButton(text="0.005 SOL", callback_data="priority_0.005"),
        InlineKeyboardButton(text="0.01 SOL", callback_data="priority_0.01"),
        InlineKeyboardButton(text="✏️ Custom", callback_data="priority_custom")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="menu_settings")
    )
    return builder.as_markup()


def get_notification_keyboard(enabled: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Buy/Sell Alerts", callback_data="notif_buy_sell"),
        InlineKeyboardButton(text="✅ Copy Trade Alerts", callback_data="notif_copy_trade")
    )
    builder.row(
        InlineKeyboardButton(text="✅ Limit Order Alerts", callback_data="notif_limit"),
        InlineKeyboardButton(text="✅ Auto Sell Alerts", callback_data="notif_autosell")
    )
    builder.row(
        InlineKeyboardButton(text="✅ Deposit/Withdraw", callback_data="notif_wallet"),
        InlineKeyboardButton(text="✅ Price Alerts", callback_data="notif_price")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="menu_settings")
    )
    return builder.as_markup()


def get_position_actions_keyboard(position_id: int, token_mint: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🟢 Buy More", callback_data=f"pos_buy_{position_id}"),
        InlineKeyboardButton(text="🔴 Sell", callback_data=f"pos_sell_{position_id}")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Set Limit Order", callback_data=f"pos_limit_{position_id}"),
        InlineKeyboardButton(text="⚡ Set Auto Sell", callback_data=f"pos_autosell_{position_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Refresh", callback_data=f"pos_refresh_{position_id}"),
        InlineKeyboardButton(text="🔙 Back", callback_data="menu_positions")
    )
    return builder.as_markup()


def get_copy_wallet_actions_keyboard(wallet_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✏️ Edit Settings", callback_data=f"copy_edit_{wallet_id}"),
        InlineKeyboardButton(text="🗑️ Remove", callback_data=f"copy_remove_{wallet_id}")
    )
    builder.row(
        InlineKeyboardButton(text="📊 View Trades", callback_data=f"copy_trades_{wallet_id}"),
        InlineKeyboardButton(text="🔙 Back", callback_data="copy_list_wallets")
    )
    return builder.as_markup()


def get_token_info_keyboard(token_mint: str) -> InlineKeyboardMarkup:
    """Keyboard for token info with buy/sell actions."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🟢 Buy", callback_data=f"token_buy_{token_mint}"),
        InlineKeyboardButton(text="🔴 Sell", callback_data=f"token_sell_{token_mint}")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Set Limit Order", callback_data=f"token_limit_{token_mint}"),
        InlineKeyboardButton(text="⚡ Set Auto Sell", callback_data=f"token_autosell_{token_mint}")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Refresh", callback_data=f"token_refresh_{token_mint}"),
        InlineKeyboardButton(text="🔙 Back", callback_data="back_main")
    )
    return builder.as_markup()


def get_back_main_keyboard() -> InlineKeyboardMarkup:
    """Simple back to main menu keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Back to Menu", callback_data="back_main")
    return builder.as_markup()
