import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN

# Create a bot and storage
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=MemoryStorage())

# Keyboard
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
bt_1 = KeyboardButton('/domain')
bt_2 = KeyboardButton('/stop')
main_kb.add(bt_1).add(bt_2)

# State class
class RemindState(StatesGroup):
    text = State()
    time = State()

# /start command handler
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Hello! To create a reminder for domain renewal , enter the command '/domain'", reply_markup=main_kb)

# /remind command handler
@dp.message_handler(commands=['domain'])
async def cmd_remind(message: types.Message):
    await message.answer("Enter domain name: ")
    await RemindState.text.set()

# /stop command handler
@dp.message_handler(commands=['stop'], state="*")
async def cmd_stop(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("The domain reminder has been cancelled. To create a new one, enter /domain")

# Text reminder handler
@dp.message_handler(state=RemindState.text)
async def get_remind_text(message: types.Message, state: FSMContext):
    text = message.text
    await message.answer("Enter the time in minutes when to send the domain renewal reminder:")
    await RemindState.time.set()
    await state.update_data(text=text)  # Storing text in the state

# Time reminder handler
@dp.message_handler(state=RemindState.time)
async def get_remind_time(message: types.Message, state: FSMContext):
    try:
        time_in_minutes = int(message.text)
        data = await state.get_data()
        text = data.get('text')

        await message.answer(f"A domain renewal reminder will be sent in {time_in_minutes} minutes: '{text}'")
        await asyncio.sleep(time_in_minutes * 60)  # Convert minutes to seconds or second or days...
        await message.answer(f"Renew your domain: '{text}'")

    except ValueError:
        await message.answer("Error! Please enter a valid number of minutes")

    finally:
        await state.finish()


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
