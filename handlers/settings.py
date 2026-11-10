from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import get_main_keyboard

from config import ADMIN_USER_ID

async def notify_admin(text: str):
    if ADMIN_USER_ID:
        from config import dp as dp_ref
        try:
            await dp_ref.bot.send_message(ADMIN_USER_ID, text)
        except:
            pass

async def cmd_settings(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Settings Menu:\n\n"
        "1. /notifications - Notification settings\n"
        "2. /trading_prefs - Trading preferences\n"
        "3. /security - Account security\n\n"
        "Use /start to return to main menu.",
        reply_markup=get_main_keyboard()
    )

# Admin States for messaging
class AdminMessageStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_message_text = State()

async def admin_message_cmd(message: types.Message, state: FSMContext):
    """Admin command to send a message to any user"""
    if message.from_user.id != ADMIN_USER_ID:
        await message.answer("You are not authorized to use this command.")
        return
    
    await message.answer(
        "Admin Message Mode:\n\n"
        "Enter the User ID you want to send a message to:",
        reply_markup=get_main_keyboard()
    )
    await state.set_state(AdminMessageStates.waiting_for_user_id)

async def process_target_user_id(message: types.Message, state: FSMContext):
    """Process the target user ID"""
    if message.from_user.id != ADMIN_USER_ID:
        return
    
    try:
        target_user_id = int(message.text.strip())
        await state.update_data(target_user_id=target_user_id)
        await message.answer(
            f"Target User ID: {target_user_id}\n\n"
            "Now enter the message you want to send:",
            reply_markup=get_main_keyboard()
        )
        await state.set_state(AdminMessageStates.waiting_for_message_text)
    except ValueError:
        await message.answer(
            "Invalid User ID. Please enter a valid numeric User ID:",
            reply_markup=get_main_keyboard()
        )

async def process_message_text(message: types.Message, state: FSMContext):
    """Process and send the message to the target user"""
    if message.from_user.id != ADMIN_USER_ID:
        return
    
    data = await state.get_data()
    target_user_id = data.get("target_user_id")
    
    if not target_user_id:
        await message.answer("Error: No target user ID. Please start over with /message", reply_markup=get_main_keyboard())
        await state.clear()
        return
    
    try:
        await message.bot.send_message(target_user_id, message.text)
        await message.answer(
            f"Message sent successfully to user {target_user_id}",
            reply_markup=get_main_keyboard()
        )
        
        activity_text = f"ADMIN MESSAGE SENT\nFrom Admin: {message.from_user.id}\nTo User: {target_user_id}"
        await notify_admin(activity_text)
    except Exception as e:
        await message.answer(
            f"Failed to send message: {str(e)}\n"
            "The user may have blocked the bot or the User ID is invalid.",
            reply_markup=get_main_keyboard()
        )
    
    await state.clear()

def register_settings_handlers(dp):
    @dp.message(Command("settings"))
    async def settings_cmd(message: types.Message, state: FSMContext):
        await cmd_settings(message, state)

    @dp.message(Command("message"))
    async def message_cmd(message: types.Message, state: FSMContext):
        await admin_message_cmd(message, state)

    @dp.message(F.text == "/message")
    async def message_text_handler(message: types.Message, state: FSMContext):
        await admin_message_cmd(message, state)

    @dp.message(AdminMessageStates.waiting_for_user_id)
    async def target_user_id_handler(message: types.Message, state: FSMContext):
        await process_target_user_id(message, state)

    @dp.message(AdminMessageStates.waiting_for_message_text)
    async def message_text_handler(message: types.Message, state: FSMContext):
        await process_message_text(message, state)
