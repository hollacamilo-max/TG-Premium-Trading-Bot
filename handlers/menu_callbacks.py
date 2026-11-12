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
    '''Register all menu callback handlers.'''
    
    @dp.callback_query(F.data == "wallet_deposit")
    async def callback_wallet_deposit(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "💰 <b>Deposit SOL</b>\n\n"
            "Send SOL to your wallet address:\n"
            "<code>YourWalletAddressHere</code>\n\n"
            "Minimum deposit: 0.01 SOL",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

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

    @dp.callback_query(F.data == "wallet_import")
    async def callback_wallet_import(callback: types.CallbackQuery, state: FSMContext):
        from handlers.start import BotStates
        await state.set_state(BotStates.waiting_for_key_import)
        await callback.message.edit_text(
            "🔑 <b>Import Wallet</b>\n\n"
            "Please send your private key (base58 format for Solana).\n\n"
            "⚠️ <b>Security Warning:</b> Only import wallets you're comfortable dedicating to this bot. "
            "Your key is encrypted at rest but importing always carries risk.",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "wallet_refresh")
    async def callback_wallet_refresh(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "🔄 <b>Refreshing Balance...</b>\n\n"
            "Fetching latest balance...",
            parse_mode="HTML",
            reply_markup=get_wallet_keyboard()
        )
        await callback.answer("Balance refreshed!")

    @dp.callback_query(F.data == "wallet_history")
    async def callback_wallet_history(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "📋 <b>Transaction History</b>\n\n"
            "No transactions yet.\n\n"
            "Your transaction history will appear here.",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "buy_by_address")
    async def callback_buy_by_address(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "🎯 <b>Buy by Token Address</b>\n\n"
            "Paste the token contract address (Solana or EVM).\n\n"
            "Example Solana: <code>So11111111111111111111111111111111111111112</code>\n"
            "Example EVM: <code>0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2</code>",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "buy_search")
    async def callback_buy_search(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "🔍 <b>Search Token</b>\n\n"
            "Enter token name or symbol to search:\n\n"
            "Example: <code>BONK</code> or <code>WIF</code>",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "buy_trending")
    async def callback_buy_trending(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "💎 <b>Trending Tokens</b>\n\n"
            "Fetching trending tokens...",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "buy_favorites")
    async def callback_buy_favorites(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "⭐ <b>Favorites</b>\n\n"
            "No favorite tokens yet.\n\n"
            "Add tokens to favorites from token info screen.",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "sell_positions")
    async def callback_sell_positions(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "💼 <b>Sell from Positions</b>\n\n"
            "You have no open positions.\n\n"
            "Buy some tokens first to see them here.",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "sell_by_address")
    async def callback_sell_by_address(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "🎯 <b>Sell by Token Address</b>\n\n"
            "Paste the token contract address to sell:",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "copy_add_wallet")
    async def callback_copy_add_wallet(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "➕ <b>Add Wallet to Copy</b>\n\n"
            "Enter the wallet address you want to copy trade:\n\n"
            "Example: <code>7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU</code>",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "copy_list_wallets")
    async def callback_copy_list_wallets(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "📋 <b>My Copy Wallets</b>\n\n"
            "No copy wallets added yet.\n\n"
            "Add a wallet to start copy trading.",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "copy_settings")
    async def callback_copy_settings(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "⚙️ <b>Copy Trade Settings</b>\n\n"
            "Configure your copy trade preferences:\n\n"
            "• Max buy amount per trade\n"
            "• Slippage tolerance\n"
            "• Auto-sell settings\n"
            "• Wallet filters",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "copy_history")
    async def callback_copy_history(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "📊 <b>Copy Trade History</b>\n\n"
            "No copy trade history yet.",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "limit_create")
    async def callback_limit_create(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "➕ <b>Create Limit Order</b>\n\n"
            "Select token and set your target price.\n\n"
            "Paste token address to start:",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "limit_list")
    async def callback_limit_list(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "📋 <b>My Limit Orders</b>\n\n"
            "No active limit orders.\n\n"
            "Create a limit order to see it here.",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "autosell_add")
    async def callback_autosell_add(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "➕ <b>Add Auto Sell Rule</b>\n\n"
            "Select the type of auto sell rule:",
            parse_mode="HTML",
            reply_markup=get_auto_sell_type_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "autosell_list")
    async def callback_autosell_list(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "📋 <b>My Auto Sell Rules</b>\n\n"
            "No auto sell rules configured.\n\n"
            "Add a rule to automatically sell at target price.",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "autosell_type_target")
    async def callback_autosell_type_target(callback: types.CallbackQuery, state: FSMContext):
        await state.update_data(autosell_type="target")
        await callback.message.edit_text(
            "🟢 <b>Target Price Auto Sell</b>\n\n"
            "Enter the target price multiplier (e.g., 2 for 2x):",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "autosell_type_stop")
    async def callback_autosell_type_stop(callback: types.CallbackQuery, state: FSMContext):
        await state.update_data(autosell_type="stop_loss")
        await callback.message.edit_text(
            "🟢 <b>Stop Loss Auto Sell</b>\n\n"
            "Enter the stop loss percentage (e.g., 20 for -20%):",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "autosell_type_take")
    async def callback_autosell_type_take(callback: types.CallbackQuery, state: FSMContext):
        await state.update_data(autosell_type="take_profit")
        await callback.message.edit_text(
            "🟢 <b>Take Profit Auto Sell</b>\n\n"
            "Enter the take profit percentage (e.g., 50 for +50%):",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "positions_refresh")
    async def callback_positions_refresh(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "🔄 <b>Refreshing Positions...</b>\n\n"
            "Fetching latest prices...",
            parse_mode="HTML",
            reply_markup=get_positions_keyboard(has_positions=False)
        )
        await callback.answer("Positions refreshed!")

    @dp.callback_query(F.data == "settings_slippage")
    async def callback_settings_slippage(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "🎯 <b>Slippage Settings</b>\n\n"
            "Select your default slippage tolerance:",
            parse_mode="HTML",
            reply_markup=get_slippage_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "settings_priority_fee")
    async def callback_settings_priority_fee(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "⚡ <b>Priority Fee Settings</b>\n\n"
            "Select your default priority fee:",
            parse_mode="HTML",
            reply_markup=get_priority_fee_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "settings_notifications")
    async def callback_settings_notifications(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "🔔 <b>Notification Settings</b>\n\n"
            "Toggle notification types:",
            parse_mode="HTML",
            reply_markup=get_notification_keyboard(enabled=True)
        )
        await callback.answer()

    @dp.callback_query(F.data == "settings_language")
    async def callback_settings_language(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "🌐 <b>Language Settings</b>\n\n"
            "Select your preferred language:\n\n"
            "• English (default)\n"
            "• Spanish\n"
            "• French\n"
            "• German\n"
            "• Chinese\n"
            "• Russian",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "settings_security")
    async def callback_settings_security(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "🔒 <b>Security Settings</b>\n\n"
            "Configure security options:\n\n"
            "• Two-factor authentication\n"
            "• Withdrawal whitelist\n"
            "• Session management\n"
            "• API key permissions",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "connect_phantom")
    async def callback_connect_phantom(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "📱 <b>Connect Phantom Wallet</b>\n\n"
            "Phantom wallet connection via deep linking:\n\n"
            "1. Open Phantom app\n"
            "2. Scan QR code or click connect\n"
            "3. Approve connection\n\n"
            "<i>Deep link integration coming soon.</i>",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "connect_solflare")
    async def callback_connect_solflare(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "🦊 <b>Connect Solflare Wallet</b>\n\n"
            "Solflare wallet connection via deep linking:\n\n"
            "1. Open Solflare app\n"
            "2. Scan QR code or click connect\n"
            "3. Approve connection\n\n"
            "<i>Deep link integration coming soon.</i>",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data.regexp(r"^slippage_"))
    async def callback_slippage(callback: types.CallbackQuery, state: FSMContext):
        value = callback.data.replace("slippage_", "")
        await state.update_data(slippage=value)
        await callback.message.edit_text(
            f"✅ <b>Slippage Updated</b>\n\n"
            f"Default slippage set to: <b>{value}%</b>",
            parse_mode="HTML",
            reply_markup=get_settings_keyboard()
        )
        await callback.answer(f"Slippage set to {value}%")

    @dp.callback_query(F.data == "slippage_custom")
    async def callback_slippage_custom(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "✏️ <b>Custom Slippage</b>\n\n"
            "Enter custom slippage percentage (e.g., 1.5):",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data.regexp(r"^priority_"))
    async def callback_priority_fee(callback: types.CallbackQuery, state: FSMContext):
        value = callback.data.replace("priority_", "")
        await state.update_data(priority_fee=value)
        await callback.message.edit_text(
            f"✅ <b>Priority Fee Updated</b>\n\n"
            f"Default priority fee set to: <b>{value} SOL</b>",
            parse_mode="HTML",
            reply_markup=get_settings_keyboard()
        )
        await callback.answer(f"Priority fee set to {value} SOL")

    @dp.callback_query(F.data == "priority_custom")
    async def callback_priority_custom(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "✏️ <b>Custom Priority Fee</b>\n\n"
            "Enter custom priority fee in SOL (e.g., 0.002):",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data.regexp(r"^notif_"))
    async def callback_notification(callback: types.CallbackQuery, state: FSMContext):
        notif_type = callback.data.replace("notif_", "")
        await callback.message.edit_text(
            f"🔔 <b>Notification Toggled</b>\n\n"
            f"{notif_type.replace('_', ' ').title()} notifications updated.",
            parse_mode="HTML",
            reply_markup=get_notification_keyboard(enabled=True)
        )
        await callback.answer(f"{notif_type} toggled")

    @dp.callback_query(F.data.regexp(r"^(buy|sell|withdraw)_amount_"))
    async def callback_amount(callback: types.CallbackQuery, state: FSMContext):
        parts = callback.data.split("_")
        action = parts[0]
        amount = float(parts[2])
        await state.update_data(selected_amount=amount, action=action)
        if action == "buy":
            await callback.message.edit_text(
                f"💰 <b>Buy Amount Selected</b>\n\n"
                f"Amount: <b>{amount} SOL</b>\n\n"
                f"Now paste the token contract address to buy:",
                parse_mode="HTML",
                reply_markup=get_back_main_keyboard()
            )
        elif action == "sell":
            await callback.message.edit_text(
                f"💰 <b>Sell Amount Selected</b>\n\n"
                f"Amount: <b>{amount} SOL</b>\n\n"
                f"Now paste the token contract address to sell:",
                parse_mode="HTML",
                reply_markup=get_back_main_keyboard()
            )
        elif action == "withdraw":
            await callback.message.edit_text(
                f"💰 <b>Withdraw Amount Selected</b>\n\n"
                f"Amount: <b>{amount} SOL</b>\n\n"
                f"Enter destination wallet address:",
                parse_mode="HTML",
                reply_markup=get_back_main_keyboard()
            )
        await callback.answer(f"Amount: {amount} SOL")

    @dp.callback_query(F.data.regexp(r"^(buy|sell|withdraw)_custom$"))
    async def callback_amount_custom(callback: types.CallbackQuery, state: FSMContext):
        action = callback.data.split("_")[0]
        await callback.message.edit_text(
            f"✏️ <b>Custom {action.title()} Amount</b>\n\n"
            f"Enter amount in SOL (e.g., 0.5):",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data.regexp(r"^token_buy_"))
    async def callback_token_buy(callback: types.CallbackQuery, state: FSMContext):
        token_mint = callback.data.replace("token_buy_", "")
        await state.update_data(token_mint=token_mint, action="buy")
        await callback.message.edit_text(
            f"🟢 <b>Buy Token</b>\n\n"
            f"Token: <code>{token_mint}</code>\n\n"
            f"Select amount to buy:",
            parse_mode="HTML",
            reply_markup=get_amount_keyboard("buy")
        )
        await callback.answer()

    @dp.callback_query(F.data.regexp(r"^token_sell_"))
    async def callback_token_sell(callback: types.CallbackQuery, state: FSMContext):
        token_mint = callback.data.replace("token_sell_", "")
        await state.update_data(token_mint=token_mint, action="sell")
        await callback.message.edit_text(
            f"🔴 <b>Sell Token</b>\n\n"
            f"Token: <code>{token_mint}</code>\n\n"
            f"Select amount to sell:",
            parse_mode="HTML",
            reply_markup=get_amount_keyboard("sell")
        )
        await callback.answer()

    @dp.callback_query(F.data.regexp(r"^token_limit_"))
    async def callback_token_limit(callback: types.CallbackQuery, state: FSMContext):
        token_mint = callback.data.replace("token_limit_", "")
        await callback.message.edit_text(
            f"📊 <b>Set Limit Order</b>\n\n"
            f"Token: <code>{token_mint}</code>\n\n"
            f"Enter target price:",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data.regexp(r"^token_autosell_"))
    async def callback_token_autosell(callback: types.CallbackQuery, state: FSMContext):
        token_mint = callback.data.replace("token_autosell_", "")
        await callback.message.edit_text(
            f"⚡ <b>Set Auto Sell</b>\n\n"
            f"Token: <code>{token_mint}</code>\n\n"
            f"Select auto sell type:",
            parse_mode="HTML",
            reply_markup=get_auto_sell_type_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data.regexp(r"^token_refresh_"))
    async def callback_token_refresh(callback: types.CallbackQuery, state: FSMContext):
        token_mint = callback.data.replace("token_refresh_", "")
        await callback.message.edit_text(
            f"🔄 <b>Refreshing Token Info...</b>\n\n"
            f"Token: <code>{token_mint}</code>",
            parse_mode="HTML",
            reply_markup=get_token_info_keyboard(token_mint)
        )
        await callback.answer("Refreshing...")

    @dp.callback_query(F.data.regexp(r"^pos_buy_"))
    async def callback_pos_buy(callback: types.CallbackQuery, state: FSMContext):
        position_id = callback.data.replace("pos_buy_", "")
        await callback.message.edit_text(
            f"🟢 <b>Buy More - Position {position_id}</b>\n\n"
            f"Select amount to buy:",
            parse_mode="HTML",
            reply_markup=get_amount_keyboard("buy")
        )
        await callback.answer()

    @dp.callback_query(F.data.regexp(r"^pos_sell_"))
    async def callback_pos_sell(callback: types.CallbackQuery, state: FSMContext):
        position_id = callback.data.replace("pos_sell_", "")
        await callback.message.edit_text(
            f"🔴 <b>Sell - Position {position_id}</b>\n\n"
            f"Select amount to sell:",
            parse_mode="HTML",
            reply_markup=get_amount_keyboard("sell")
        )
        await callback.answer()

    @dp.callback_query(F.data.regexp(r"^pos_limit_"))
    async def callback_pos_limit(callback: types.CallbackQuery, state: FSMContext):
        position_id = callback.data.replace("pos_limit_", "")
        await callback.message.edit_text(
            f"📊 <b>Set Limit Order - Position {position_id}</b>\n\n"
            f"Enter target price:",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data.regexp(r"^pos_autosell_"))
    async def callback_pos_autosell(callback: types.CallbackQuery, state: FSMContext):
        position_id = callback.data.replace("pos_autosell_", "")
        await callback.message.edit_text(
            f"⚡ <b>Set Auto Sell - Position {position_id}</b>\n\n"
            f"Select auto sell type:",
            parse_mode="HTML",
            reply_markup=get_auto_sell_type_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data.regexp(r"^pos_refresh_"))
    async def callback_pos_refresh(callback: types.CallbackQuery, state: FSMContext):
        position_id = callback.data.replace("pos_refresh_", "")
        await callback.answer(f"Refreshing position {position_id}...")

    @dp.callback_query(F.data.regexp(r"^copy_edit_"))
    async def callback_copy_edit(callback: types.CallbackQuery, state: FSMContext):
        wallet_id = callback.data.replace("copy_edit_", "")
        await callback.message.edit_text(
            f"✏️ <b>Edit Copy Wallet {wallet_id}</b>\n\n"
            f"Configure copy settings for this wallet:",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data.regexp(r"^copy_remove_"))
    async def callback_copy_remove(callback: types.CallbackQuery, state: FSMContext):
        wallet_id = callback.data.replace("copy_remove_", "")
        await callback.message.edit_text(
            f"🗑️ <b>Remove Copy Wallet {wallet_id}</b>\n\n"
            f"Are you sure you want to remove this wallet?",
            parse_mode="HTML",
            reply_markup=get_confirm_keyboard("copy_remove", f"copy_remove_confirm_{wallet_id}", "copy_list_wallets")
        )
        await callback.answer()

    @dp.callback_query(F.data.regexp(r"^copy_remove_confirm_"))
    async def callback_copy_remove_confirm(callback: types.CallbackQuery, state: FSMContext):
        wallet_id = callback.data.replace("copy_remove_confirm_", "")
        await callback.message.edit_text(
            f"✅ <b>Wallet Removed</b>\n\n"
            f"Copy wallet {wallet_id} has been removed.",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer("Wallet removed")

    @dp.callback_query(F.data.regexp(r"^copy_trades_"))
    async def callback_copy_trades(callback: types.CallbackQuery, state: FSMContext):
        wallet_id = callback.data.replace("copy_trades_", "")
        await callback.message.edit_text(
            f"📊 <b>Copy Trades - Wallet {wallet_id}</b>\n\n"
            f"No trades yet for this wallet.",
            parse_mode="HTML",
            reply_markup=get_back_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data.regexp(r"^captcha_"))
    async def callback_captcha(callback: types.CallbackQuery, state: FSMContext):
        action = callback.data.replace("captcha_", "")
        if action == "refresh":
            await callback.answer("Generating new captcha...")
        elif action == "verify":
            await callback.answer("Verifying...")
        else:
            await callback.answer(f"Selected: {action}")

    print("✅ All menu callbacks registered!")
