@from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_trading_keyboard(chain: str, wallet_id: int) -> InlineKeyboardMarkup:
    """Main trading keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🟢 Buy", callback_data=f"trade_buy_{wallet_id}"),
        InlineKeyboardButton(text="🔴 Sell", callback_data=f"trade_sell_{wallet_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Swap", callback_data=f"trade_swap_{wallet_id}"),
        InlineKeyboardButton(text="📋 Limit Order", callback_data=f"trade_limit_{wallet_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="📊 Positions", callback_data=f"trade_positions_{wallet_id}"),
        InlineKeyboardButton(text="📈 History", callback_data=f"trade_history_{wallet_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="🎯 Set Slippage", callback_data=f"trade_slippage_{wallet_id}"),
        InlineKeyboardButton(text="⛽ Gas Settings", callback_data=f"trade_gas_{wallet_id}"),
    )
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data=f"wallet_{wallet_id}"))
    
    return builder.as_markup()


def get_slippage_keyboard(current_slippage: float, wallet_id: int) -> InlineKeyboardMarkup:
    """Slippage selection keyboard."""
    builder = InlineKeyboardBuilder()
    
    slippages = [0.1, 0.5, 1, 2, 3, 5, 10, 20]
    row = []
    for slippage in slippages:
        text = f"{slippage}%" + (" ✅" if abs(slippage - current_slippage) < 0.01 else "")
        row.append(InlineKeyboardButton(text=text, callback_data=f"set_slippage_{slippage}_{wallet_id}"))
        if len(row) == 3:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)
    
    builder.row(
        InlineKeyboardButton(text="✏️ Custom", callback_data=f"slippage_custom_{wallet_id}"),
    )
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data=f"trade_menu_{wallet_id}"))
    
    return builder.as_markup()


def get_amount_keyboard(wallet_id: int, token_symbol: str, balance: str, trade_type: str) -> InlineKeyboardMarkup:
    """Amount input keyboard with quick buttons."""
    builder = InlineKeyboardBuilder()
    
    # Quick percentage buttons
    percentages = [10, 25, 50, 75, 100]
    row = []
    for pct in percentages:
        row.append(InlineKeyboardButton(text=f"{pct}%", callback_data=f"amount_pct_{pct}_{wallet_id}_{trade_type}"))
        if len(row) == 3:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)
    
    builder.row(
        InlineKeyboardButton(text="✏️ Custom Amount", callback_data=f"amount_custom_{wallet_id}_{trade_type}"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data=f"trade_{trade_type}_{wallet_id}"),
    )
    
    return builder.as_markup()


def get_token_select_keyboard(tokens: list, wallet_id: int, action: str, page: int = 0) -> InlineKeyboardMarkup:
    """Token selection keyboard with pagination."""
    builder = InlineKeyboardBuilder()
    
    per_page = 8
    start = page * per_page
    end = start + per_page
    page_tokens = tokens[start:end]
    
    for token in page_tokens:
        symbol = token.get("symbol", "UNK")
        address = token.get("address", "")
        builder.row(InlineKeyboardButton(
            text=f"${symbol} ({address[:6]}...{address[-4:]})",
            callback_data=f"token_{action}_{address}_{wallet_id}"
        ))
    
    # Pagination
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Prev", callback_data=f"token_page_{page-1}_{wallet_id}_{action}"))
    if end < len(tokens):
        nav_row.append(InlineKeyboardButton(text="Next ▶️", callback_data=f"token_page_{page+1}_{wallet_id}_{action}"))
    if nav_row:
        builder.row(*nav_row)
    
    builder.row(
        InlineKeyboardButton(text="🔍 Search Token", callback_data=f"token_search_{wallet_id}_{action}"),
        InlineKeyboardButton(text="📋 Paste Address", callback_data=f"token_paste_{wallet_id}_{action}"),
    )
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data=f"trade_{action}_{wallet_id}"))
    
    return builder.as_markup()


def get_confirm_trade_keyboard(wallet_id: int, trade_type: str) -> InlineKeyboardMarkup:
    """Trade confirmation keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Confirm", callback_data=f"confirm_{trade_type}_{wallet_id}"),
        InlineKeyboardButton(text="❌ Cancel", callback_data=f"trade_{trade_type}_{wallet_id}"),
    )
    
    return builder.as_markup()


def get_dex_select_keyboard(wallet_id: int, chain: str) -> InlineKeyboardMarkup:
    """DEX selection keyboard."""
    builder = InlineKeyboardBuilder()
    
    if chain in ["ethereum", "base", "arbitrum", "bsc", "polygon", "avalanche"]:
        builder.row(
            InlineKeyboardButton(text="🦄 Uniswap V2", callback_data=f"dex_uniswap_v2_{wallet_id}"),
            InlineKeyboardButton(text="🦄 Uniswap V3", callback_data=f"dex_uniswap_v3_{wallet_id}"),
        )
        builder.row(
            InlineKeyboardButton(text="🔍 1inch (Best Rate)", callback_data=f"dex_1inch_{wallet_id}"),
        )
    elif chain in ["solana"]:
        builder.row(
            InlineKeyboardButton(text="🪐 Jupiter (Best Rate)", callback_data=f"dex_jupiter_{wallet_id}"),
            InlineKeyboardButton(text="🌊 Raydium", callback_data=f"dex_raydium_{wallet_id}"),
        )
        builder.row(
            InlineKeyboardButton(text="🐳 Orca", callback_data=f"dex_orca_{wallet_id}"),
        )
    
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data=f"trade_menu_{wallet_id}"))
    
    return builder.as_markup()
