import asyncio
from aiogram import Bot, Dispatcher, types
from config import *
from agent import run_agent

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message()
async def start_handler(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    print("start agent")
    response = await run_agent(message)
    print("agent is done")
    await message.answer(response)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
