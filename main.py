import json
import random
import time
import os
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA_FILE = "players.json"

# загрузка данных
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# сохранение
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

players = load_data()

# создание игрока
def get_player(uid):

    uid = str(uid)

    if uid not in players:
        players[uid] = {
            "coins": 200,
            "last_train": 0,
            "last_daily": 0,
            "stadium": 1,
            "team": {
                "striker": 1,
                "midfielder": 1,
                "defender": 1,
                "goalkeeper": 1
            }
        }

    return players[uid]

# сила команды
def calculate_power(player):

    team = player["team"]

    power = (
        team["striker"] * 2 +
        team["midfielder"] * 2 +
        team["defender"] * 2 +
        team["goalkeeper"] * 2 +
        player["stadium"]
    )

    return power


# клавиатура
menu = ReplyKeyboardMarkup(
keyboard=[
[KeyboardButton(text="👤 Профиль"),KeyboardButton(text="⚽ Матч")],
[KeyboardButton(text="🏋️ Тренировка"),KeyboardButton(text="🎁 Сундук")],
[KeyboardButton(text="🏆 Турнир"),KeyboardButton(text="🎁 Бонус")],
[KeyboardButton(text="🧑 Купить игрока"),KeyboardButton(text="🎒 Инвентарь")],
[KeyboardButton(text="🏟 Улучшить стадион"),KeyboardButton(text="📊 Топ")]
],
resize_keyboard=True
)

# старт
@dp.message(Command("start"))
async def start(message: types.Message):

    get_player(message.from_user.id)
    save_data(players)

    await message.answer(
        "⚽ Добро пожаловать в футбольную игру!",
        reply_markup=menu
    )


# профиль
@dp.message(lambda m: m.text == "👤 Профиль")
async def profile(message: types.Message):

    player = get_player(message.from_user.id)
    power = calculate_power(player)

    await message.answer(
        f"👤 Профиль\n\n"
        f"💰 Монеты: {player['coins']}\n"
        f"⚡ Сила команды: {power}\n"
        f"🏟 Стадион: {player['stadium']}"
    )


# матч
@dp.message(lambda m: m.text == "⚽ Матч")
async def match(message: types.Message):

    player = get_player(message.from_user.id)

    power = calculate_power(player)

    win_chance = 40 + power * 4
    result = random.randint(1,100)

    if result <= win_chance:

        reward = random.randint(40,100)
        player["coins"] += reward

        text = f"🏆 Победа!\n+{reward} монет"

    else:

        text = "❌ Вы проиграли матч"

    save_data(players)

    await message.answer(text)


# тренировка
@dp.message(lambda m: m.text == "🏋️ Тренировка")
async def train(message: types.Message):

    player = get_player(message.from_user.id)

    cooldown = 600
    now = time.time()

    if now - player["last_train"] < cooldown:

        remain = int(cooldown - (now - player["last_train"]))

        minutes = remain // 60
        seconds = remain % 60

        await message.answer(
            f"⏳ Следующая тренировка через {minutes}м {seconds}с"
        )
        return

    cost = 30

    if player["coins"] < cost:

        await message.answer("❌ Нужно 30 монет")
        return

    player["coins"] -= cost

    position = random.choice(["striker","midfielder","defender","goalkeeper"])

    player["team"][position] += 1

    player["last_train"] = now

    save_data(players)

    await message.answer(
        f"🏋️ Тренировка успешна!\n"
        f"Игрок улучшил позицию: {position}"
    )


# сундук
@dp.message(lambda m: m.text == "🎁 Сундук")
async def chest(message: types.Message):

    player = get_player(message.from_user.id)

    chest = random.choice(["common","rare","legend"])

    if chest == "common":

        reward = random.randint(20,50)
        name = "📦 Обычный сундук"

    elif chest == "rare":

        reward = random.randint(50,120)
        name = "💎 Редкий сундук"

    else:

        reward = random.randint(120,250)
        name = "👑 Легендарный сундук"

    player["coins"] += reward

    save_data(players)

    await message.answer(
        f"{name}\nВы получили {reward} монет!"
    )


# турнир
@dp.message(lambda m: m.text == "🏆 Турнир")
async def tournament(message: types.Message):

    player = get_player(message.from_user.id)

    cost = 80

    if player["coins"] < cost:

        await message.answer("❌ Нужно 80 монет")
        return

    player["coins"] -= cost

    wins = random.randint(0,3)

    reward = wins * 100

    player["coins"] += reward

    save_data(players)

    await message.answer(
        f"🏆 Турнир завершен\n"
        f"Побед: {wins}\n"
        f"Награда: {reward}"
    )


# ежедневный бонус
@dp.message(lambda m: m.text == "🎁 Бонус")
async def daily(message: types.Message):

    player = get_player(message.from_user.id)

    now = time.time()

    if now - player["last_daily"] < 86400:

        remain = int(86400 - (now - player["last_daily"]))

        hours = remain // 3600

        await message.answer(
            f"⏳ Бонус через {hours} часов"
        )
        return

    reward = random.randint(100,200)

    player["coins"] += reward
    player["last_daily"] = now

    save_data(players)

    await message.answer(
        f"🎁 Вы получили {reward} монет!"
    )


# покупка игрока
@dp.message(lambda m: m.text == "🧑 Купить игрока")
async def buy_player(message: types.Message):

    player = get_player(message.from_user.id)

    cost = 120

    if player["coins"] < cost:

        await message.answer("❌ Нужно 120 монет")
        return

    position = random.choice(["striker","midfielder","defender","goalkeeper"])

    player["coins"] -= cost

    player["team"][position] += 1

    save_data(players)

    await message.answer(
        f"⚽ Новый игрок!\n"
        f"Позиция: {position}"
    )


# инвентарь
@dp.message(lambda m: m.text == "🎒 Инвентарь")
async def inventory(message: types.Message):

    player = get_player(message.from_user.id)

    team = player["team"]

    await message.answer(
        f"👥 Команда\n\n"
        f"⚽ Нападающие: {team['striker']}\n"
        f"🎯 Полузащитники: {team['midfielder']}\n"
        f"🛡 Защитники: {team['defender']}\n"
        f"🧤 Вратари: {team['goalkeeper']}\n\n"
        f"🏟 Стадион: {player['stadium']}"
    )


# стадион
@dp.message(lambda m: m.text == "🏟 Улучшить стадион")
async def stadium(message: types.Message):

    player = get_player(message.from_user.id)

    cost = player["stadium"] * 200

    if player["coins"] < cost:

        await message.answer(
            f"❌ Нужно {cost} монет"
        )
        return

    player["coins"] -= cost
    player["stadium"] += 1

    save_data(players)

    await message.answer(
        f"🏟 Стадион улучшен!\n"
        f"Уровень: {player['stadium']}"
    )


# топ
@dp.message(lambda m: m.text == "📊 Топ")
async def top(message: types.Message):

    ranking = sorted(
        players.items(),
        key=lambda x: calculate_power(x[1]),
        reverse=True
    )[:10]

    text = "🏆 Топ игроков\n\n"

    i = 1

    for uid,data in ranking:

        power = calculate_power(data)

        text += f"{i}. ⚡ {power} | 💰 {data['coins']}\n"

        i += 1

    await message.answer(text)


async def main():

    await dp.start_polling(bot)

asyncio.run(main())
