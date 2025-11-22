@dp.message_handler(commands=['claude_ping'])
async def ping(message: types.Message):
    from claude_client import claude_ping
    result = claude_ping()
    await message.reply(f"Claude says: {result}")