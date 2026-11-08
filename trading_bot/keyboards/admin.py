@from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Admin panel main keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👥 All Users", callback_data="admin_users"),
        InlineKeyboardButton(text="📊 System Stats", callback_data="admin_stats"),
    )
    builder.row(
        InlineKeyboardButton(text="📝 Activity Log", callback_data="admin_activity"),
        InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast"),
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ Bot Settings", callback_data="admin_settings"),
        InlineKeyboardButton(text="💰 Revenue", callback_data="admin_revenue"),
    )
    builder.row(InlineKeyboardButton(text="🔙 Back to Main", callback_data="main_menu"))
    
    return builder.as_markup()


def get_admin_user_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Admin user detail keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👛 View Wallets", callback_data=f"admin_user_wallets_{user_id}"),
        InlineKeyboardButton(text="📈 Trade History", callback_data=f"admin_user_trades_{user_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="📝 Activity Log", callback_data=f"admin_user_activity_{user_id}"),
        InlineKeyboardButton(text="💰 Referral Stats", callback_data=f"admin_user_referrals_{user_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="🚫 Ban User", callback_data=f"admin_ban_{user_id}"),
        InlineKeyboardButton(text="✅ Unban User", callback_data=f"admin_unban_{user_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="📩 Send Message", callback_data=f"admin_message_{user_id}"),
    )
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="admin_users"))
    
    return builder.as_markup()


def get_broadcast_keyboard() -> InlineKeyboardMarkup:
    """Broadcast message keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📢 All Users", callback_data="broadcast_all"),
        InlineKeyboardButton(text="👤 Specific User", callback_data="broadcast_user"),
    )
    builder.row(
        InlineKeyboardButton(text="💎 Premium Only", callback_data="broadcast_premium"),
        InlineKeyboardButton(text="🆕 New Users (24h)", callback_data="broadcast_new"),
    )
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="admin_panel"))
    
    return builder.as_markup()


def get_admin_activity_keyboard() -> InlineKeyboardMarkup:
    """Admin activity log filter keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔑 Wallet Imports", callback_data="admin_activity_wallet_import"),
        InlineKeyboardButton(text="💰 Trades", callback_data="admin_activity_trade"),
    )
    builder.row(
        InlineKeyboardButton(text="💬 Messages", callback_data="admin_activity_message"),
        InlineKeyboardButton(text="🤖 Commands", callback_data="admin_activity_command"),
    )
    builder.row(
        InlineKeyboardButton(text="📋 All Activity", callback_data="admin_activity_all"),
    )
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="admin_panel"))
    
    return builder.as_markup()
