from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import get_main_keyboard

from config import ADMIN_USER_ID

class BuyStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_confirmation = State()

async def notify_admin(text: str):
    if ADMIN_USER_ID:
        from config import dp as dp_ref
        try:
            await dp_ref.bot.send_message(ADMIN_USER_ID, text)
        except:
            pass

def register_buy_handlers(dp):
    @dp.message(F.text.in_(["/solana", "/evm"]))
    async def process_chain_selection(message: types.Message, state: FSMContext):
        data = await state.get_data()
        chain = data.get("chain", "unknown")
        
        activity_text = f"💰 BUY REQUEST\nUser: {message.from_user.id}\nChain: {chain}"
        await notify_admin(activity_text)
        
        await message.answer(
            f"Buy order on {chain} chain!\n\n"
            "Please enter the amount:",
            reply_markup=get_main_keyboard()
        )
        await state.set_state(BuyStates.waiting_for_amount)

    @dp.message()  # Amount input
    async def process_buy_amount(message: types.Message, state: FSMContext):
        if (await state.get_state()) == BuyStates.waiting_for_amount:
            amount = message.text
            data = await state.get_data()
            chain = data.get("chain", "unknown")
            
            activity_text = f"💰 BUY ORDER\nUser: {message.from_user.id}\nChain: {chain}\nAmount: {amount}"
            await notify_admin(activity_text)
            
            await message.answer(
                f"Processing buy order:\n"
                f"Chain: {chain}\n"
                f"Amount: {amount}\n\n"
                "Please confirm the transaction details.",
                reply_markup=get_main_keyboard()
            )
            await state.clear()