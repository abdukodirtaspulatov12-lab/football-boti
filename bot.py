import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "ТВОЙ_ТОКЕН_БОТА"

bot = Bot(token=TOKEN)
dp = Dispatcher()

users = {}

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⚽ Играть")],
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🏆 Рейтинг")],
        [KeyboardButton(text="🛒 Магазин")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id

    if user_id not in users:
        users[user_id] = {
            "coins": 100,
            "wins": 0
        }

    await message.answer(
        "⚽ Добро пожаловать в футбольную игру!",
        reply_markup=menu
    )

@dp.message(lambda message: message.text == "👤 Профиль")
async def profile(message: types.Message):
    user = users.get(message.from_user.id)

    text = (
        f"👤 Профиль\n\n"
        f"💰 Монеты: {user['coins']}\n"
        f"🏆 Победы: {user['wins']}"
    )

    await message.answer(text)

@dp.message(lambda message: message.text == "⚽ Играть")
async def play(message: types.Message):
    import random

    goal = random.choice([True, False])

    if goal:
        users[message.from_user.id]["coins"] += 10
        users[message.from_user.id]["wins"] += 1
        await message.answer("🥅 ГООООЛ! +10 монет")
    else:
        await message.answer("❌ Мимо ворот!")

@dp.message(lambda message: message.text == "🏆 Рейтинг")
async def rating(message: types.Message):

    sorted_users = sorted(
        users.items(),
        key=lambda x: x[1]["wins"],
        reverse=True
    )

    text = "🏆 Рейтинг игроков\n\n"

    for i, (uid, data) in enumerate(sorted_users[:10], start=1):
        text += f"{i}. {data['wins']} побед\n"

    await message.answer(text)

@dp.message(lambda message: message.text == "🛒 Магазин")
async def shop(message: types.Message):

    text = (
        "🛒 Магазин\n\n"
        "⚽ Мяч — 50 монет\n"
        "🥅 Перчатки — 100 монет"
    )

    await message.answer(text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
