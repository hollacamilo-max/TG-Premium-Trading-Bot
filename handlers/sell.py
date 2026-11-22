from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import get_main_keyboard

from config import get_settings

settings = get_settings()

class SellStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_confirmation = State()

async def notify_admin(bot, text: str):
    if settings.ADMIN_IDS:
        try:
            await bot.send_message(settings.ADMIN_IDS[0], text)
        except:
            pass

def register_sell_handlers(dp):
    @dp.message(F.text.in_(['/solana', '/evm']))
    async def process_chain_selection(message: types.Message, state: FSMContext):
        data = await state.get_data()
        chain = data.get('chain', 'unknown')
        
        activity_text = 'SELL REQUEST\nUser: ' + str(message.from_user.id) + '\nChain: ' + chain
        await notify_admin(message.bot, activity_text)
        
        await message.answer(
            'Sell order on ' + chain + ' chain!\n\n' +
            'Please enter the amount:',
            reply_markup=get_main_keyboard()
        )
        await state.set_state(SellStates.waiting_for_amount)

    @dp.message(SellStates.waiting_for_amount)
    async def process_sell_amount(message: types.Message, state: FSMContext):
        amount = message.text
        data = await state.get_data()
        chain = data.get('chain', 'unknown')
        
        activity_text = 'SELL ORDER\nUser: ' + str(message.from_user.id) + '\nChain: ' + chain + '\nAmount: ' + amount
        await notify_admin(message.bot, activity_text)
        
        await message.answer(
            'Processing sell order:\n' +
            'Chain: ' + chain + '\n' +
            'Amount: ' + amount + '\n\n' +
            'Please confirm the transaction details.',
            reply_markup=get_main_keyboard()
        )
        await state.clear()
