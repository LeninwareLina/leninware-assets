import os
from aiogram import Bot, Dispatcher, types, executor

from claude_client import claude_ping

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.reply("Leninware online.\nUse /claude_ping to test Claude connectivity.")

@dp.message_handler(commands=["claude_ping"])
async def ping_cmd(message: types.Message):
    response = claude_ping()
    await message.reply(f"Claude says: {response}")

if __name__ == "__main__":
    executor.start_polling(dp)