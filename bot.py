import os
import asyncio
import random
import json

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

DB = "players.json"

# ===== Загрузка базы =====
def load():
    try:
        with open(DB, "r") as f:
            return json.load(f)
    except:
        return {}

def save():
    with open(DB, "w") as f:
        json.dump(players, f)

players = load()

# ===== Меню =====
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⚽ Матч"), KeyboardButton(text="🤖 ИИ матч")],
        [KeyboardButton(text="👥 PvP")],
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🎒 Инвентарь")],
        [KeyboardButton(text="🏆 Рейтинг"), KeyboardButton(text="🛒 Магазин")]
    ],
    resize_keyboard=True
)

# ===== Предметы =====
items = {
    "мяч": {"price":50, "power":1, "rarity":"обычный"},
    "бутсы": {"price":120, "power":2, "rarity":"обычный"},
    "перчатки": {"price":200, "power":3, "rarity":"редкий"},
    "золотой мяч": {"price":500, "power":5, "rarity":"легендарный"}
}

# ===== Регистрация =====
def register(user):
    uid = str(user.id)

    if uid not in players:
        players[uid] = {
            "name": user.first_name,
            "coins": 200,
            "wins": 0,
            "power": 1,
            "inventory": []
        }
        save()

# ===== START =====
@dp.message(Command("start"))
async def start(message: types.Message):

    register(message.from_user)

    await message.answer(
        "⚽ Добро пожаловать в футбольную игру!",
        reply_markup=menu
    )

# ===== ПРОФИЛЬ =====
@dp.message(lambda m: m.text == "👤 Профиль")
async def profile(message: types.Message):

    uid = str(message.from_user.id)

    if uid not in players:
        register(message.from_user)

    p = players[uid]

    text = (
        f"👤 Игрок: {p['name']}\n\n"
        f"💰 Монеты: {p['coins']}\n"
        f"🏆 Победы: {p['wins']}\n"
        f"⚡ Сила: {p['power']}"
    )

    await message.answer(text)

# ===== ИНВЕНТАРЬ =====
@dp.message(lambda m: m.text == "🎒 Инвентарь")
async def inventory(message: types.Message):

    uid = str(message.from_user.id)

    if uid not in players:
        register(message.from_user)

    inv = players[uid]["inventory"]

    if not inv:
        await message.answer("🎒 Инвентарь пуст")
        return

    text = "🎒 Твои предметы:\n\n"

    for i in inv:
        text += f"• {i}\n"

    await message.answer(text)

# ===== МАГАЗИН =====
@dp.message(lambda m: m.text == "🛒 Магазин")
async def shop(message: types.Message):

    text = "🛒 Магазин\n\n"

    for name,data in items.items():
        text += f"{name} — {data['price']} монет ({data['rarity']})\n"

    text += "\nНапиши: купить название"

    await message.answer(text)

# ===== ПОКУПКА =====
@dp.message(lambda m: m.text and m.text.lower().startswith("купить"))
async def buy(message: types.Message):

    uid = str(message.from_user.id)

    if uid not in players:
        register(message.from_user)

    p = players[uid]

    name = message.text.lower().replace("купить ","")

    if name not in items:
        await message.answer("❌ Предмет не найден")
        return

    item = items[name]

    if p["coins"] < item["price"]:
        await message.answer("❌ Недостаточно монет")
        return

    p["coins"] -= item["price"]
    p["power"] += item["power"]
    p["inventory"].append(name)

    save()

    await message.answer(f"✅ Куплен предмет: {name}")
# ===== ОБЫЧНЫЙ МАТЧ =====
@dp.message(lambda m: m.text == "⚽ Матч")
async def match(message: types.Message):

    uid = str(message.from_user.id)

    if uid not in players:
        register(message.from_user)

    p = players[uid]

    enemy_power = random.randint(1,5)

    player_goals = 0
    enemy_goals = 0

    await message.answer("⚽ Матч начинается!")

    await asyncio.sleep(1)

    for i in range(3):

        await message.answer(f"🎯 Удар {i+1}")

        player_shot = random.randint(1, p["power"] + 2)
        enemy_shot = random.randint(1, enemy_power + 2)

        if player_shot > enemy_shot:

            player_goals += 1
            await message.answer("⚽ ГООООЛ!!! 🥅🔥")

        else:

            enemy_goals += 1
            await message.answer("🧤 Вратарь отбил! 😱")

        await asyncio.sleep(1)

    result = ""

    if player_goals > enemy_goals:

        p["wins"] += 1
        p["coins"] += 30
        result = "🏆 Победа! +30 монет"

    elif player_goals < enemy_goals:

        result = "❌ Поражение"

    else:

        result = "🤝 Ничья"

    save()

    await message.answer(
        f"🏁 Матч окончен!\n\n"
        f"Ты: {player_goals}\n"
        f"Соперник: {enemy_goals}\n\n"
        f"{result}"
    )
# ===== ИИ МАТЧ =====
@dp.message(lambda m: m.text == "🤖 ИИ матч")
async def ai_match(message: types.Message):

    uid = str(message.from_user.id)

    if uid not in players:
        register(message.from_user)

    p = players[uid]

    enemy = random.randint(1,7)

    if p["power"] >= enemy:

        p["wins"] += 1
        p["coins"] += 30
        result = "🥅 Победа! +30 монет"

    else:

        result = "❌ Поражение"

    save()

    await message.answer(
        f"🤖 Матч против ИИ\n\n"
        f"Твоя сила: {p['power']}\n"
        f"Сила ИИ: {enemy}\n\n"
        f"{result}"
    )

# ===== PvP =====
waiting_player = None

@dp.message(lambda m: m.text == "👥 PvP")
async def pvp(message: types.Message):

    global waiting_player

    uid = str(message.from_user.id)

    if uid not in players:
        register(message.from_user)

    if waiting_player is None:

        waiting_player = uid
        await message.answer("⏳ Ожидание второго игрока...")
        return

    if waiting_player == uid:
        await message.answer("❌ Нужен другой игрок")
        return

    p1 = players[waiting_player]
    p2 = players[uid]

    power1 = p1["power"]
    power2 = p2["power"]

    if power1 >= power2:
        winner = p1
    else:
        winner = p2

    winner["wins"] += 1
    winner["coins"] += 50

    save()

    await message.answer(
        f"⚔ PvP матч!\n\n"
        f"{p1['name']} сила: {power1}\n"
        f"{p2['name']} сила: {power2}\n\n"
        f"🏆 Победитель: {winner['name']}"
    )

    waiting_player = None

# ===== РЕЙТИНГ =====
@dp.message(lambda m: m.text == "🏆 Рейтинг")
async def rating(message: types.Message):

    top = sorted(players.items(), key=lambda x: x[1]["wins"], reverse=True)

    text = "🏆 Топ игроков\n\n"

    for i,(uid,p) in enumerate(top[:10],1):
        text += f"{i}. {p['name']} — {p['wins']} побед\n"

    await message.answer(text)

# ===== ЗАПУСК =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
