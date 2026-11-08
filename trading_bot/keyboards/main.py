from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_keyboard(has_wallets: bool = False, is_admin: bool = False, is_premium: bool = False) -> InlineKeyboardMarkup:
    """Main menu keyboard - Maestro style."""
    builder = InlineKeyboardBuilder()
    
    # First row - Trading & Wallets (main actions)
    if has_wallets:
        builder.row(
            InlineKeyboardButton(text="💰 Trade", callback_data="trade_menu"),
            InlineKeyboardButton(text="👛 Wallets", callback_data="wallets_menu"),
        )
    else:
        builder.row(InlineKeyboardButton(text="👛 Import Wallet", callback_data="import_wallet_start"))
    
    # Second row - Portfolio & Positions
    builder.row(
        InlineKeyboardButton(text="📊 Portfolio", callback_data="portfolio"),
        InlineKeyboardButton(text="📈 Positions", callback_data="positions"),
    )
    
    # Third row - Copy Trade & Sniper (premium features)
    if is_premium:
        builder.row(
            InlineKeyboardButton(text="👥 Copy Trade", callback_data="copy_trade_menu"),
            InlineKeyboardButton(text="🎯 Sniper", callback_data="sniper_menu"),
        )
    
    # Fourth row - History & Referral
    builder.row(
        InlineKeyboardButton(text="📋 History", callback_data="trade_history"),
        InlineKeyboardButton(text="👥 Referral", callback_data="referral_menu"),
    )
    
    # Fifth row - Settings & Tools
    builder.row(
        InlineKeyboardButton(text="⚙️ Settings", callback_data="settings"),
        InlineKeyboardButton(text="🔧 Tools", callback_data="tools_menu"),
    )
    
    # Admin panel
    if is_admin:
        builder.row(InlineKeyboardButton(text="🔐 Admin Panel", callback_data="admin_panel"))
    
    # Help row
    builder.row(InlineKeyboardButton(text="ℹ️ Help", callback_data="help"))
    
    return builder.as_markup()


def get_wallet_keyboard(wallets: list, chain_filter: str = None, selected_wallet_id: int = None) -> InlineKeyboardMarkup:
    """Wallet management keyboard."""
    builder = InlineKeyboardBuilder()
    
    for wallet in wallets:
        chain_emoji = "🔷" if wallet.chain.value == "evm" else "🟣" if wallet.chain.value == "solana" else "🔵"
        default_badge = " ⭐" if wallet.is_default else ""
        balance = wallet.balance_cache.get("native", "0") if wallet.balance_cache else "0"
        # Mark selected wallet
        prefix = "✅ " if selected_wallet_id and wallet.id == selected_wallet_id else ""
        builder.row(InlineKeyboardButton(
            text=f"{prefix}{chain_emoji} {wallet.name or wallet.chain.value.capitalize()} {default_badge} ({balance[:8]})",
            callback_data=f"wallet_{wallet.id}"
        ))
    
    builder.row(InlineKeyboardButton(text="➕ Import New Wallet", callback_data="import_wallet_start"))
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="main_menu"))
    
    return builder.as_markup()


def get_chain_keyboard() -> InlineKeyboardMarkup:
    """Chain selection keyboard for wallet import."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔷 Ethereum", callback_data="import_chain_ethereum"),
        InlineKeyboardButton(text="🔷 Base", callback_data="import_chain_base"),
    )
    builder.row(
        InlineKeyboardButton(text="🔷 Arbitrum", callback_data="import_chain_arbitrum"),
        InlineKeyboardButton(text="🔷 BSC", callback_data="import_chain_bsc"),
    )
    builder.row(
        InlineKeyboardButton(text="🔷 Polygon", callback_data="import_chain_polygon"),
        InlineKeyboardButton(text="🔷 Avalanche", callback_data="import_chain_avalanche"),
    )
    builder.row(InlineKeyboardButton(text="🟣 Solana", callback_data="import_chain_solana"))
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="import_wallet_start"))
    
    return builder.as_markup()


def get_wallet_type_keyboard(chain: str) -> InlineKeyboardMarkup:
    """Wallet type selection keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📝 Seed Phrase (12/24 words)", callback_data=f"import_type_seed_{chain}"),
    )
    builder.row(
        InlineKeyboardButton(text="🔐 Private Key", callback_data=f"import_type_pk_{chain}"),
    )
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="import_wallet_start"))
    
    return builder.as_markup()


def get_wallet_detail_keyboard(wallet_id: int, is_default: bool = False) -> InlineKeyboardMarkup:
    """Wallet detail actions keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💰 Trade", callback_data=f"trade_wallet_{wallet_id}"),
        InlineKeyboardButton(text="📤 Send", callback_data=f"send_wallet_{wallet_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="📥 Receive", callback_data=f"receive_wallet_{wallet_id}"),
        InlineKeyboardButton(text="🔄 Refresh", callback_data=f"wallet_refresh_{wallet_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="⭐ Set Default", callback_data=f"wallet_default_{wallet_id}"),
        InlineKeyboardButton(text="✏️ Rename", callback_data=f"wallet_rename_{wallet_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="🗑️ Delete", callback_data=f"wallet_delete_{wallet_id}"),
    )
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="wallets_menu"))
    
    return builder.as_markup()


def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Settings keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🎯 Slippage", callback_data="setting_slippage"),
        InlineKeyboardButton(text="⛽ Gas Settings", callback_data="setting_gas"),
    )
    builder.row(
        InlineKeyboardButton(text="🔔 Notifications", callback_data="setting_notifications"),
        InlineKeyboardButton(text="🌐 Language", callback_data="setting_language"),
    )
    builder.row(
        InlineKeyboardButton(text="🔐 Security", callback_data="setting_security"),
        InlineKeyboardButton(text="📊 Auto Buy/Sell", callback_data="setting_auto_trade"),
    )
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="main_menu"))
    
    return builder.as_markup()


def get_tools_keyboard() -> InlineKeyboardMarkup:
    """Tools menu keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔍 Token Scanner", callback_data="tool_scanner"),
        InlineKeyboardButton(text="📊 Price Alerts", callback_data="tool_alerts"),
    )
    builder.row(
        InlineKeyboardButton(text="💱 Bridge", callback_data="tool_bridge"),
        InlineKeyboardButton(text="🔐 Revoke Access", callback_data="tool_revoke"),
    )
    builder.row(
        InlineKeyboardButton(text="📱 Wallet Connect", callback_data="tool_walletconnect"),
        InlineKeyboardButton(text="📝 Tax Report", callback_data="tool_tax"),
    )
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="main_menu"))
    
    return builder.as_markup()


def get_positions_keyboard(has_positions: bool = False) -> InlineKeyboardMarkup:
    """Positions/Portfolio keyboard."""
    builder = InlineKeyboardBuilder()
    
    if has_positions:
        builder.row(
            InlineKeyboardButton(text="📈 All Positions", callback_data="positions_all"),
            InlineKeyboardButton(text="💰 PnL Summary", callback_data="positions_pnl"),
        )
        builder.row(
            InlineKeyboardButton(text="🔄 Refresh All", callback_data="positions_refresh"),
            InlineKeyboardButton(text="📤 Export", callback_data="positions_export"),
        )
    else:
        builder.row(InlineKeyboardButton(text="📭 No open positions", callback_data="noop"))
    
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="main_menu"))
    
    return builder.as_markup()


def get_copy_trade_keyboard() -> InlineKeyboardMarkup:
    """Copy Trade keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👥 Top Traders", callback_data="copy_top_traders"),
        InlineKeyboardButton(text="📊 My Copies", callback_data="copy_my_copies"),
    )
    builder.row(
        InlineKeyboardButton(text="➕ Add Trader", callback_data="copy_add_trader"),
        InlineKeyboardButton(text="⚙️ Copy Settings", callback_data="copy_settings"),
    )
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="main_menu"))
    
    return builder.as_markup()


def get_sniper_keyboard() -> InlineKeyboardMarkup:
    """Sniper/New Token keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🎯 New Pairs", callback_data="sniper_new_pairs"),
        InlineKeyboardButton(text="📋 My Snipes", callback_data="sniper_my_snipes"),
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ Sniper Settings", callback_data="sniper_settings"),
        InlineKeyboardButton(text="🔍 Filter", callback_data="sniper_filter"),
    )
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="main_menu"))
    
    return builder.as_markup()


def get_trade_history_keyboard() -> InlineKeyboardMarkup:
    """Trade history keyboard with filters."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📊 All Trades", callback_data="history_all"),
        InlineKeyboardButton(text="✅ Successful", callback_data="history_success"),
    )
    builder.row(
        InlineKeyboardButton(text="❌ Failed", callback_data="history_failed"),
        InlineKeyboardButton(text="⏳ Pending", callback_data="history_pending"),
    )
    builder.row(
        InlineKeyboardButton(text="📅 Today", callback_data="history_today"),
        InlineKeyboardButton(text="📅 This Week", callback_data="history_week"),
    )
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="main_menu"))
    
    return builder.as_markup()
