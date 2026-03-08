# mega_football_bot.py
import os
import random
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ====== Токен через переменную окружения ======
API_TOKEN = os.getenv("API_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ====== Игроки ======
players = {}  # player_id: {"money": int, "level": int, "stamina": int, "xp": int, "items": list, "tournaments": int, "rating": int, "last_daily": datetime}

# ====== Магазин ======
shop_items = {
    "Energy Drink": {"price": 50, "effect": "stamina+20", "rarity": "common"},
    "Golden Boots": {"price": 200, "effect": "level+1", "rarity": "rare"},
    "Magic Ball": {"price": 150, "effect": "xp+50", "rarity": "rare"},
    "Shield": {"price": 100, "effect": "stamina+30", "rarity": "common"},
    "Lucky Charm": {"price": 250, "effect": "xp+100", "rarity": "epic"},
    "Wizard Gloves": {"price": 500, "effect": "stamina+50", "rarity": "epic"}
}

# ====== Сундуки ======
chests = [
    {"name": "Малый сундук", "price": 50, "reward_money": (10, 100), "reward_xp": (5, 30), "chance": 0.9},
    {"name": "Средний сундук", "price": 200, "reward_money": (100, 300), "reward_xp": (20, 80), "chance": 0.7},
    {"name": "Большой сундук", "price": 500, "reward_money": (300, 1000), "reward_xp": (80, 200), "chance": 0.5},
    {"name": "Легендарный сундук", "price": 1000, "reward_money": (500, 5000), "reward_xp": (200, 500), "chance": 0.3}
]

# ====== Турниры ======
tournaments = [
    {"name": "Local League", "level_req": 1, "reward_money": 100, "reward_xp": 50},
    {"name": "National Cup", "level_req": 3, "reward_money": 300, "reward_xp": 120},
    {"name": "Champions Tournament", "level_req": 5, "reward_money": 1000, "reward_xp": 500}
]

# ====== Функции ======
def get_player(user_id):
    if user_id not in players:
        players[user_id] = {
            "money": 100,
            "level": 1,
            "stamina": 100,
            "xp": 0,
            "items": [],
            "tournaments": 0,
            "rating": 1000,
            "last_daily": datetime.min
        }
    return players[user_id]

def match_outcome(player, opponent):
    chance = player["level"] * random.randint(1, 6) + player["stamina"] // 10 + random.randint(0,10)
    opp_chance = opponent["level"] * random.randint(1, 6) + opponent["stamina"] // 10 + random.randint(0,10)
    # Случайные события
    event = random.choice(["none","injury","super_goal","bonus_money"])
    event_msg = ""
    goal_msg = ""
    if random.random() < 0.5:
        goal_msg = "⚽ Гол!"
    else:
        goal_msg = "❌ Промах!"
    if event == "injury":
        player["stamina"] -= 20
        event_msg = "😢 Травма! Stamina -20"
    elif event == "super_goal":
        chance += 10
        event_msg = "⚡ Супер-гол! +10 к шансам"
    elif event == "bonus_money":
        bonus = random.randint(10,50)
        player["money"] += bonus
        event_msg = f"💰 Бонусная монета! +{bonus} денег"
    
    outcome = "win" if chance >= opp_chance else "lose"
    return outcome, event_msg, goal_msg

def apply_item_effect(player, effect):
    if "stamina" in effect:
        player["stamina"] += int(effect.split("+")[1])
    if "level" in effect:
        player["level"] += int(effect.split("+")[1])
    if "xp" in effect:
        player["xp"] += int(effect.split("+")[1])

def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="⚽ Играть матч", callback_data="play_match")
    kb.button(text="🆚 PvP матч", callback_data="pvp_match")
    kb.button(text="🏪 Магазин", callback_data="shop")
    kb.button(text="🎁 Сундуки", callback_data="chests")
    kb.button(text="🏆 Турниры", callback_data="tournaments")
    kb.button(text="👤 Профиль", callback_data="profile")
    kb.button(text="📊 Статистика", callback_data="stats")
    kb.button(text="🎯 Ежедневный бонус", callback_data="daily")
    return kb.as_markup()

# ====== Команды ======
@dp.message(Command(commands=["start"]))
async def start(message: types.Message):
    get_player(message.from_user.id)
    await message.answer("Привет! Добро пожаловать в Mega Football Bot Ultimate! Выбери действие:", reply_markup=main_menu())

# ====== Игровой матч против ИИ ======
@dp.callback_query(lambda c: c.data == "play_match")
async def play_match(call: types.CallbackQuery):
    user = get_player(call.from_user.id)
    opponent = {"level": random.randint(1, 5), "stamina": random.randint(50, 100)}
    outcome, event_msg, goal_msg = match_outcome(user, opponent)
    reward = random.randint(50, 150)
    
    if outcome == "win":
        user["money"] += reward
        user["xp"] += 20
        user["stamina"] -= 20
        msg = f"{goal_msg} Ты выиграл матч против ИИ! 💰 +{reward} монет, XP +20, Stamina -20"
    else:
        user["xp"] += 10
        user["stamina"] -= 30
        msg = f"{goal_msg} Ты проиграл 😢 XP +10, Stamina -30"
    
    if event_msg:
        msg += f"\n{event_msg}"
    
    kb = InlineKeyboardBuilder()
    kb.button(text="Вернуться в меню", callback_data="menu")
    await call.message.edit_text(msg, reply_markup=kb.as_markup())

# ====== PvP матч ======
@dp.callback_query(lambda c: c.data == "pvp_match")
async def pvp_match(call: types.CallbackQuery):
    user = get_player(call.from_user.id)
    other_ids = [uid for uid in players if uid != call.from_user.id]
    if not other_ids:
        await call.message.edit_text("Пока нет других игроков для PvP 😢", reply_markup=main_menu())
        return
    opponent_id = random.choice(other_ids)
    opponent = get_player(opponent_id)
    
    outcome, event_msg, goal_msg = match_outcome(user, opponent)
    reward = random.randint(50, 200)
    
    if outcome == "win":
        user["money"] += reward
        user["xp"] += 25
        user["stamina"] -= 25
        user["rating"] += 15
        opponent["stamina"] -= 20
        opponent["rating"] -= 10
        msg = f"{goal_msg} Ты выиграл PvP матч! 💰 +{reward}, XP +25, Stamina -25, Рейтинг +15"
    else:
        user["xp"] += 10
        user["stamina"] -= 30
        user["rating"] -= 10
        msg = f"{goal_msg} Ты проиграл PvP матч 😢 XP +10, Stamina -30, Рейтинг -10"
    
    if event_msg:
        msg += f"\n{event_msg}"
    
    kb = InlineKeyboardBuilder()
    kb.button(text="Вернуться в меню", callback_data="menu")
    await call.message.edit_text(msg, reply_markup=kb.as_markup())

# ====== Профиль ======
@dp.callback_query(lambda c: c.data == "profile")
async def profile(call: types.CallbackQuery):
    user = get_player(call.from_user.id)
    msg = (f"👤 Профиль игрока:\n"
           f"💰 Деньги: {user['money']}\n"
           f"⚡ Stamina: {user['stamina']}\n"
           f"📈 Уровень: {user['level']}\n"
           f"⭐ XP: {user['xp']}\n"
           f"🏆 Турниров: {user['tournaments']}\n"
           f"🏅 Рейтинг: {user['rating']}\n"
           f"🎒 Предметы: {', '.join(user['items']) if user['items'] else 'Нет'}")
    kb = InlineKeyboardBuilder()
    kb.button(text="Вернуться в меню", callback_data="menu")
    await call.message.edit_text(msg, reply_markup=kb.as_markup())

# ====== Ежедневный бонус ======
@dp.callback_query(lambda c: c.data == "daily")
async def daily_bonus(call: types.CallbackQuery):
    user = get_player(call.from_user.id)
    now = datetime.now()
    if now - user["last_daily"] >= timedelta(hours=24):
        money_bonus = random.randint(50,200)
        xp_bonus = random.randint(20,100)
        user["money"] += money_bonus
        user["xp"] += xp_bonus
        user["last_daily"] = now
        msg = f"🎁 Ежедневный бонус! 💰 +{money_bonus}, XP +{xp_bonus}"
    else:
        remaining = timedelta(hours=24) - (now - user["last_daily"])
        msg = f"⏳ Ежедневный бонус уже взят. Осталось: {remaining}"
    kb = InlineKeyboardBuilder()
    kb.button(text="Вернуться в меню", callback_data="menu")
    await call.message.edit_text(msg, reply_markup=kb.as_markup())

# ====== Сундуки ======
@dp.callback_query(lambda c: c.data == "chests")
async def open_chests(call: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for chest in chests:
        kb.button(text=f"{chest['name']} - {chest['price']} 💰", callback_data=f"open_{chest['name']}")
    kb.button(text="Вернуться в меню", callback_data="menu")
    await call.message.edit_text("Выберите сундук для открытия:", reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith("open_"))
async def open_chest(call: types.CallbackQuery):
    chest_name = call.data.replace("open_", "")
    chest = next(c for c in chests if c["name"] == chest_name)
    user = get_player(call.from_user.id)
    if user["money"] >= chest["price"]:
        user["money"] -= chest["price"]
        if random.random() <= chest["chance"]:
            money_reward = random.randint(*chest["reward_money"])
            xp_reward = random.randint(*chest["reward_xp"])
            user["money"] += money_reward
            user["xp"] += xp_reward
            msg = f"🎉 {chest_name} открыт! 💰 +{money_reward}, XP +{xp_reward}"
        else:
            msg = f"❌ {chest_name} пустой... Повезёт в следующий раз!"
    else:
        msg = "Недостаточно денег 💸"
    kb = InlineKeyboardBuilder()
    kb.button(text="Вернуться в сундуки", callback_data="chests")
    kb.button(text="Вернуться в меню", callback_data="menu")
    await call.message.edit_text(msg, reply_markup=kb.as_markup())

# ====== Магазин ======
@dp.callback_query(lambda c: c.data == "shop")
async def shop(call: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for item_name, info in shop_items.items():
        kb.button(text=f"{item_name} - {info['price']} 💰 ({info['rarity']})", callback_data=f"buy_{item_name}")
    kb.button(text="Вернуться в меню", callback_data="menu")
    await call.message.edit_text("Добро пожаловать в магазин! Выберите предмет:", reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith("buy_"))
async def buy_item(call: types.CallbackQuery):
    item_name = call.data.replace("buy_", "")
    user = get_player(call.from_user.id)
    item = shop_items[item_name]
    if user["money"] >= item["price"]:
        user["money"] -= item["price"]
        user["items"].append(item_name)
        apply_item_effect(user, item["effect"])
        msg = f"✅ Вы купили {item_name}"
    else:
        msg = "Недостаточно денег 💸"
    kb = InlineKeyboardBuilder()
    kb.button(text="Вернуться в магазин", callback_data="shop")
    kb.button(text="Вернуться в меню", callback_data="menu")
    await call.message.edit_text(msg, reply_markup=kb.as_markup())

# ====== Турниры ======
@dp.callback_query(lambda c: c.data == "tournaments")
async def tournaments_menu(call: types.CallbackQuery):
    user = get_player(call.from_user.id)
    kb = InlineKeyboardBuilder()
    for t in tournaments:
        kb.button(text=f"{t['name']} (Lvl {t['level_req']})", callback_data=f"tournament_{t['name']}")
    kb.button(text="Вернуться в меню", callback_data="menu")
    await call.message.edit_text("Выберите турнир:", reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith("tournament_"))
async def tournament_match(call: types.CallbackQuery):
    t_name = call.data.replace("tournament_", "")
    tournament = next(t for t in tournaments if t["name"] == t_name)
    user = get_player(call.from_user.id)
    if user["level"] < tournament["level_req"]:
        await call.message.edit_text("😢 Твой уровень слишком низкий для этого турнира", reply_markup=main_menu())
        return
    opponent = {"level": tournament["level_req"] + random.randint(0,2), "stamina": random.randint(50,100)}
    outcome, event_msg, goal_msg = match_outcome(user, opponent)
    if outcome == "win":
        user["money"] += tournament["reward_money"]
        user["xp"] += tournament["reward_xp"]
        user["stamina"] -= 30
        user["tournaments"] += 1
        user["rating"] += 20
        msg = f"{goal_msg} Ты выиграл турнир {t_name}! 💰 +{tournament['reward_money']}, XP +{tournament['reward_xp']}, Stamina -30, Рейтинг +20"
    else:
        user["xp"] += 15
        user["stamina"] -= 40
        user["rating"] -= 10
        msg = f"{goal_msg} Ты проиграл турнир {t_name} 😢 XP +15, Stamina -40, Рейтинг -10"
    if event_msg:
        msg += f"\n{event_msg}"
    kb = InlineKeyboardBuilder()
    kb.button(text="Вернуться в меню", callback_data="menu")
    await call.message.edit_text(msg, reply_markup=kb.as_markup())

# ====== Статистика ======
@dp.callback_query(lambda c: c.data == "stats")
async def stats(call: types.CallbackQuery):
    user = get_player(call.from_user.id)
    msg = (f"📊 Статистика игрока:\n"
           f"💰 Деньги: {user['money']}\n"
           f"⚡ Stamina: {user['stamina']}\n"
           f"📈 Уровень: {user['level']}\n"
           f"⭐ XP: {user['xp']}\n"
           f"🏆 Турниров: {user['tournaments']}\n"
           f"🏅 Рейтинг: {user['rating']}\n"
           f"🎒 Предметы: {', '.join(user['items']) if user['items'] else 'Нет'}")
    kb = InlineKeyboardBuilder()
    kb.button(text="Вернуться в меню", callback_data="menu")
    await call.message.edit_text(msg, reply_markup=kb.as_markup())

# ====== Вернуться в меню ======
@dp.callback_query(lambda c: c.data == "menu")
async def menu(call: types.CallbackQuery):
    await call.message.edit_text("Главное меню:", reply_markup=main_menu())

# ====== Запуск бота ======
if __name__ == "__main__":
    print("Mega Football Bot Ultimate RPG запущен!")
    asyncio.run(dp.start_polling(bot))
