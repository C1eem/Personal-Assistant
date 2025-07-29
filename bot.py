import asyncio
import os
from aiogram import Bot, Dispatcher, types
from config import *
from dotenv import load_dotenv
from DeepSeekR1 import DeepSeekAPI
from agent import run_agent

load_dotenv()

bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher()
model = DeepSeekAPI(os.environ["DEEP_API_TOKEN"])


@dp.message()
async def start_handler(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    print("start agent")
    response = await run_agent(message)  # Добавляем await
    print("agent is done")
    await message.answer(response)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
