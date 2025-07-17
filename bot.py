import asyncio
from aiogram import Bot, Dispatcher, types
from config import *
from zeroshot import ZeroShotClassifier

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
model = ZeroShotClassifier()

@dp.message()
async def start_handler(message: types.Message):
    ans = model.classify(text=message.text, candidate_labels=LABELS)
    await message.answer(ans)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
