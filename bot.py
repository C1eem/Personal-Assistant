import asyncio
from aiogram import Bot, Dispatcher, types
from config import *
from DeepSeekR1 import DeepSeekAPI

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
model = DeepSeekAPI(DEEP_API_TOKEN)

@dp.message()
async def start_handler(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    response = model.ask(text=message.text, labels=LABELS)
    await message.answer(response)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
