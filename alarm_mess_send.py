from options import API_TOKEN
from aiogram import Bot, Dispatcher, types
import asyncio
from aiogram.utils import executor
from telegrapBOT import userID

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


def get_users():
    yield from userID


async def send_message(user_id: int, text: str, disable_notification: bool = False) -> bool:
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)
    except Exception as E:
        print(E)
    else:
        return True
    return False


async def broadcaster(mess) -> int:
    # count = 0
    try:
        for user_id in get_users():
            if await send_message(user_id, mess):
                pass
                # count += 1
            await asyncio.sleep(3)
    finally:
        pass

    # return count




if __name__ == '__main__':
    executor.start(dp, broadcaster())