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
        with open(DB,"r") as f:
            return json.load(f)
    except:
        return {}

def save():
    with open(DB,"w") as f:
        json.dump(players,f)

players = load()


# ===== Регистрация =====

def register(user):

    uid = str(user.id)

    if uid not in players:

        players[uid] = {
            "name": user.first_name,
            "coins": 200,
            "wins": 0,
            "power": 1,
            "inventory": [],
            "last_daily":0
        }

        save()


# ===== Меню =====

menu = ReplyKeyboardMarkup(
keyboard=[
[KeyboardButton(text="⚽ Матч"),KeyboardButton(text="🎯 Пенальти")],
[KeyboardButton(text="🤖 ИИ матч"),KeyboardButton(text="👥 PvP")],
[KeyboardButton(text="📦 Сундук"),KeyboardButton(text="🎁 Награда")],
[KeyboardButton(text="👤 Профиль"),KeyboardButton(text="🎒 Инвентарь")],
[KeyboardButton(text="🏆 Рейтинг"),KeyboardButton(text="🛒 Магазин")]
],
resize_keyboard=True
)


# ===== Предметы =====

items = {

"мяч":{"price":50,"power":1,"rarity":"обычный"},
"бутсы":{"price":120,"power":2,"rarity":"обычный"},
"перчатки":{"price":200,"power":3,"rarity":"редкий"},
"золотой мяч":{"price":500,"power":5,"rarity":"легендарный"}

}


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
    register(message.from_user)

    p = players[uid]

    await message.answer(
f"👤 {p['name']}\n\n"
f"💰 Монеты: {p['coins']}\n"
f"🏆 Победы: {p['wins']}\n"
f"⚡ Сила: {p['power']}"
)


# ===== ИНВЕНТАРЬ =====

@dp.message(lambda m: m.text == "🎒 Инвентарь")
async def inventory(message: types.Message):

    uid = str(message.from_user.id)

    inv = players[uid]["inventory"]

    if not inv:

        await message.answer("🎒 Инвентарь пуст")
        return

    text = "🎒 Предметы:\n\n"

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

    await message.answer(f"✅ Куплен предмет {name}")


# ===== МАТЧ =====

@dp.message(lambda m: m.text == "⚽ Матч")
async def match(message: types.Message):

    uid = str(message.from_user.id)

    p = players[uid]

    enemy = random.randint(1,6)

    pg = 0
    eg = 0

    await message.answer("🏟 Матч начинается!")

    for i in range(5):

        await asyncio.sleep(1)

        event = random.randint(1,3)

        if event == 1:

            await message.answer("⚡ Ты атакуешь")

            if random.randint(1,p["power"]+2) > random.randint(1,enemy+2):

                pg += 1
                await message.answer("⚽ ГОООЛ")

            else:

                await message.answer("🧤 Сейв")

        elif event == 2:

            await message.answer("😈 Соперник атакует")

            if random.randint(1,enemy+2) > random.randint(1,p["power"]+2):

                eg += 1
                await message.answer("🥅 Гол соперника")

            else:

                await message.answer("🧤 Ты спас")

        else:

            await message.answer("⚔ Борьба в центре")

    if pg > eg:

        p["wins"] += 1
        p["coins"] += 40
        result = "🏆 Победа"

    elif pg < eg:

        result = "❌ Поражение"

    else:

        result = "🤝 Ничья"

    save()

    await message.answer(
f"🏁 Конец матча\n\n"
f"{pg}:{eg}\n\n"
f"{result}"
)


# ===== ПЕНАЛЬТИ =====

@dp.message(lambda m: m.text == "🎯 Пенальти")
async def penalty(message: types.Message):

    goals = 0

    for i in range(3):

        await asyncio.sleep(1)

        if random.randint(1,2) == 1:

            goals += 1
            await message.answer("⚽ Гол")

        else:

            await message.answer("🧤 Сейв")

    await message.answer(f"Забито {goals}/3")


# ===== СУНДУК =====

@dp.message(lambda m: m.text == "📦 Сундук")
async def chest(message: types.Message):

    uid = str(message.from_user.id)

    p = players[uid]

    rarity = random.randint(1,100)

    if rarity <= 60:

        coins = random.randint(20,40)
        p["coins"] += coins

        result = f"💰 {coins} монет"

    elif rarity <= 90:

        item = random.choice(list(items.keys()))
        p["inventory"].append(item)

        result = f"🎁 Предмет: {item}"

    else:

        p["coins"] += 100
        result = "⭐ ЛЕГЕНДАРНЫЙ ПРИЗ 100 монет"

    save()

    await message.answer(result)


# ===== НАГРАДА =====

@dp.message(lambda m: m.text == "🎁 Награда")
async def daily(message: types.Message):

    uid = str(message.from_user.id)

    p = players[uid]

    coins = random.randint(20,60)

    p["coins"] += coins

    save()

    await message.answer(f"🎁 Ежедневная награда {coins} монет")


# ===== РЕЙТИНГ =====

@dp.message(lambda m: m.text == "🏆 Рейтинг")
async def rating(message: types.Message):

    top = sorted(players.items(), key=lambda x:x[1]["wins"], reverse=True)

    text = "🏆 Топ игроков\n\n"

    for i,(uid,p) in enumerate(top[:10],1):

        text += f"{i}. {p['name']} — {p['wins']}\n"

    await message.answer(text)


# ===== ЗАПУСК =====

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
