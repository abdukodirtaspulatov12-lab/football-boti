import os
import random
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ====== Токен ======
API_TOKEN = os.getenv("API_TOKEN")  # ставь токен через Render или Replit Variables
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ====== Игроки ======
players = {}  # user_id: {money, level, stamina, xp, items, skins, rating, last_daily, last_training}

# ====== Скины ======
skins = {
    "⚡ Золотые бутсы": {"effect": "goal+20", "rarity": "rare"},
    "🛡 Щит ворот": {"effect": "defense+15", "rarity": "rare"},
    "🎩 Магическая шляпа": {"effect": "bonus_money+50", "rarity": "epic"},
    "🔥 Огненный мяч": {"effect": "goal+30", "rarity": "epic"},
    "🌟 Легендарные перчатки": {"effect": "defense+30", "rarity": "legendary"},
    "💰 Монетный пояс": {"effect": "bonus_money+200", "rarity": "legendary"}
}

# ====== Магазин ======
shop_items = {
    "Energy Drink": {"price": 50, "effect": "stamina+20", "rarity": "common"},
    "Lucky Charm": {"price": 200, "effect": "xp+50", "rarity": "rare"},
    "Golden Gloves": {"price": 500, "effect": "defense+25", "rarity": "epic"},
    "Legendary Boots": {"price": 1000, "effect": "goal+40", "rarity": "legendary"}
}

# ====== Сундуки ======
chests = [
    {"name":"Малый сундук","price":50,"rewards":[("money",(10,100)),("xp",(5,30))],"chance":[0.8,0.8]},
    {"name":"Средний сундук","price":200,"rewards":[("money",(100,300)),("xp",(20,80))],"chance":[0.7,0.7]},
    {"name":"Большой сундук","price":500,"rewards":[("money",(300,1000)),("xp",(80,200))],"chance":[0.5,0.5]},
    {"name":"Легендарный сундук","price":1000,"rewards":[("money",(500,5000)),("xp",(200,500)),("skin","legendary")],"chance":[0.3,0.3,0.2]}
]

# ====== Турниры ======
tournaments = [
    {"name":"Local League","level_req":1,"reward_money":100,"reward_xp":50},
    {"name":"National Cup","level_req":3,"reward_money":300,"reward_xp":120},
    {"name":"Champions Tournament","level_req":5,"reward_money":1000,"reward_xp":500}
]

# ====== PvP Действия ======
actions = ["Атаковать ⚽", "Защищаться 🛡", "Супер-удар ⚡"]

# ====== Игровые функции ======
def get_player(uid):
    if uid not in players:
        players[uid] = {
            "money":100,
            "level":1,
            "stamina":100,
            "xp":0,
            "items":[],
            "skins":[],
            "rating":1000,
            "last_daily":datetime.min,
            "last_training":datetime.min
        }
    return players[uid]

def match_outcome(player, opponent, skin_effects=None):
    bonus_goal = 0
    bonus_def = 0
    bonus_money = 0
    if skin_effects:
        for e in skin_effects:
            effect = skins.get(e, {}).get("effect", "")
            if "goal" in effect: bonus_goal += int(effect.split("+")[1])
            if "defense" in effect: bonus_def += int(effect.split("+")[1])
            if "bonus_money" in effect: bonus_money += int(effect.split("+")[1])
    
    player_score = player["level"] + random.randint(1,6) + bonus_goal
    opp_score = opponent["level"] + random.randint(1,6) + bonus_def
    goal_msg = "⚽ Гол!" if random.random() < 0.6 else "❌ Промах!"
    
    outcome = "win" if player_score >= opp_score else "lose"
    reward_money = random.randint(50,200)+bonus_money
    return outcome, goal_msg, reward_money

def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="⚽ Играть матч", callback_data="play_match")
    kb.button(text="🆚 PvP матч", callback_data="pvp_match")
    kb.button(text="🏋️‍♂️ Тренировка", callback_data="training")
    kb.button(text="🏪 Магазин", callback_data="shop")
    kb.button(text="🎁 Сундуки", callback_data="chests")
    kb.button(text="🏆 Турниры", callback_data="tournaments")
    kb.button(text="👤 Профиль", callback_data="profile")
    kb.button(text="🎯 Ежедневный бонус", callback_data="daily")
    return kb.as_markup()

# ====== Старт ======
@dp.message(Command(commands=["start"]))
async def start(message: types.Message):
    get_player(message.from_user.id)
    await message.answer("Привет! Добро пожаловать в Mega Football RPG! Выбери действие:", reply_markup=main_menu())

# ====== Матч против ИИ ======
@dp.callback_query(lambda c: c.data=="play_match")
async def play_match(call: types.CallbackQuery):
    user = get_player(call.from_user.id)
    opponent = {"level":random.randint(1,5)}
    outcome, goal_msg, reward = match_outcome(user, opponent, user["skins"])
    
    if outcome=="win":
        user["money"] += reward
        user["xp"] += 20
        user["stamina"] -= 20
        msg = f"{goal_msg} Ты выиграл матч! 💰 +{reward}, XP +20, Stamina -20"
    else:
        user["xp"] += 10
        user["stamina"] -= 25
        msg = f"{goal_msg} Ты проиграл 😢 XP +10, Stamina -25"
    
    kb = InlineKeyboardBuilder()
    kb.button(text="Вернуться в меню", callback_data="menu")
    await call.message.edit_text(msg, reply_markup=kb.as_markup())

# ====== PvP матч ======
@dp.callback_query(lambda c: c.data=="pvp_match")
async def start_pvp(call: types.CallbackQuery):
    user = get_player(call.from_user.id)
    if len(players)<2:
        await call.message.edit_text("Недостаточно игроков для PvP 😢", reply_markup=main_menu())
        return
    opp_id = random.choice([uid for uid in players if uid!=call.from_user.id])
    opponent = players[opp_id]
    await call.message.edit_text("🏟 PvP Матч начался! Выберите действие:")
    await next_pvp_round(call, user, opponent, 1, 0, 0)

async def next_pvp_round(call, user, opponent, round_num, user_score, opp_score):
    if round_num>3:
        if user_score>opp_score:
            user["money"] += 200
            user["xp"] += 50
            user["rating"] += 20
            opponent["rating"] -= 20
            msg = f"🏆 Победа! Счёт: {user_score} - {opp_score}\n💰 +200, XP +50, Рейтинг +20"
        elif user_score<opp_score:
            user["xp"] += 25
            user["rating"] -= 10
            opponent["rating"] += 10
            msg = f"😢 Проигрыш! Счёт: {user_score} - {opp_score}\nXP +25, Рейтинг -10"
        else:
            msg = f"🤝 Ничья! Счёт: {user_score} - {opp_score}\nXP +20"
        kb = InlineKeyboardBuilder()
        kb.button(text="Вернуться в меню", callback_data="menu")
        await call.message.edit_text(msg, reply_markup=kb.as_markup())
        return
    
    kb = InlineKeyboardBuilder()
    for act in actions:
        kb.button(text=act, callback_data=f"pvp_act_{act}_{round_num}_{user_score}_{opp_score}")
    await call.message.edit_text(f"Раунд {round_num}/3. Выберите действие:", reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith("pvp_act_"))
async def handle_pvp_action(call: types.CallbackQuery):
    parts = call.data.split("_")
    action = parts[2]
    round_num = int(parts[3])
    user_score = int(parts[4])
    opp_score = int(parts[5])
    
    user = get_player(call.from_user.id)
    opp_id = random.choice([uid for uid in players if uid!=call.from_user.id])
    opponent = players[opp_id]
    
    opp_action = random.choice(actions)
    
    u_goal = random.random() < (0.6 if action=="Атаковать ⚽" else 0.3 if action=="Защищаться 🛡" else 0.5)
    o_goal = random.random() < (0.6 if opp_action=="Атаковать ⚽" else 0.3 if opp_action=="Защищаться 🛡" else 0.5)
    
    user_score += 1 if u_goal else 0
    opp_score += 1 if o_goal else 0
    
    round_msg = (f"Раунд {round_num}:\n"
                 f"Ты: {'⚽' if u_goal else '❌'} {user_score}\n"
                 f"Соперник: {'⚽' if o_goal else '❌'} {opp_score}\n"
                 f"Твой ход: {action}\nСоперник: {opp_action}")
    
    await call.message.edit_text(round_msg)
    await asyncio.sleep(1)
    await next_pvp_round(call, user, opponent, round_num+1, user_score, opp_score)

# ====== Тренировка каждые 10 минут ======
@dp.callback_query(lambda c: c.data=="training")
async def training(call: types.CallbackQuery):
    user = get_player(call.from_user.id)
    now = datetime.now()
    if now - user["last_training"] < timedelta(minutes=10):
        remaining = timedelta(minutes=10) - (now - user["last_training"])
        mins, secs = divmod(remaining.seconds, 60)
        await call.message.edit_text(f"⏳ Подождите {mins} мин {secs} сек до следующей тренировки")
        return
    
    anim = ["🏃‍♂️","💨","⚽","🥅"]
    msg = "Тренировка началась!\n"
    sent = await call.message.edit_text(msg)
    for i in range(4):
        await asyncio.sleep(0.7)
        await sent.edit_text(msg+" ".join(anim[:i+1]))
    
    xp_gain = random.randint(10,25)
    stamina_gain = random.randint(15,30)
    user["xp"] += xp_gain
    user["stamina"] += stamina_gain
    user["last_training"] = now
    
    kb = InlineKeyboardBuilder()
    kb.button(text="Вернуться в меню", callback_data="menu")
    await sent.edit_text(f"✅ Тренировка завершена! XP +{xp_gain}, Stamina +{stamina_gain}", reply_markup=kb.as_markup())

# ====== Профиль ======
@dp.callback_query(lambda c: c.data=="profile")
async def profile(call: types.CallbackQuery):
    user = get_player(call.from_user.id)
    skins_list = ', '.join(user['skins']) if user['skins'] else 'Нет'
    items_list = ', '.join(user['items']) if user['items'] else 'Нет'
    msg = (f"👤 Профиль:\n💰 Деньги: {user['money']}\n⚡ Stamina: {user['stamina']}\n"
           f"📈 Уровень: {user['level']}\n⭐ XP: {user['xp']}\n🏅 Рейтинг: {user['rating']}\n"
           f"🎒 Предметы: {items_list}\n👟 Скины: {skins_list}")
    kb = InlineKeyboardBuilder()
    kb.button(text="Вернуться в меню", callback_data="menu")
    await call.message.edit_text(msg, reply_markup=kb.as_markup())

# ====== Сундуки ======
@dp.callback_query(lambda c: c.data=="chests")
async def open_chests_menu(call: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for i,ch in enumerate(chests):
        kb.button(text=f"{ch['name']} 💰{ch['price']}", callback_data=f"open_chest_{i}")
    kb.button(text="Назад в меню", callback_data="menu")
    await call.message.edit_text("Выберите сундук для открытия:", reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith("open_chest_"))
async def open_chest(call: types.CallbackQuery):
    idx = int(call.data.split("_")[-1])
    chest = chests[idx]
    user = get_player(call.from_user.id)
    if user["money"]<chest["price"]:
        await call.message.edit_text("❌ Недостаточно денег!", reply_markup=main_menu())
        return
    user["money"] -= chest["price"]
    msg = f"Открываем {chest['name']}...\n"
    sent = await call.message.edit_text(msg)
    anim = ["🔒","🗝","🎁"]
    for a in anim:
        await asyncio.sleep(0.5)
        await sent.edit_text(msg+a)
    
    rewards_msg = "Ты получил:\n"
    for i, (rtype, rrange) in enumerate(chest["rewards"]):
        if random.random()<=chest["chance"][i]:
            if rtype=="money":
                gain = random.randint(*rrange)
                user["money"] += gain
                rewards_msg += f"💰 {gain} монет\n"
            elif rtype=="xp":
                gain = random.randint(*rrange)
                user["xp"] += gain
                rewards_msg += f"⭐ {gain} XP\n"
            elif rtype=="skin":
                possible = [s for s,v in skins.items() if v["rarity"]=="legendary"]
                if possible:
                    skin_gain = random.choice(possible)
                    user["skins"].append(skin_gain)
                    rewards_msg += f"👟 Скин {skin_gain}\n"
    kb = InlineKeyboardBuilder()
    kb.button(text="Вернуться в меню", callback_data="menu")
    await sent.edit_text(rewards_msg, reply_markup=kb.as_markup())

# ====== Ежедневный бонус ======
@dp.callback_query(lambda c: c.data=="daily")
async def daily_bonus(call: types.CallbackQuery):
    user = get_player(call.from_user.id)
    now = datetime.now()
    if now - user["last_daily"] < timedelta(hours=24):
        remaining = timedelta(hours=24) - (now - user["last_daily"])
        h, m = divmod(remaining.seconds//60,60)
        await call.message.edit_text(f"⏳ Ежедневный бонус доступен через {h}ч {m}м")
        return
    money = random.randint(50,200)
    xp = random.randint(20,50)
    user["money"] += money
    user["xp"] += xp
    user["last_daily"] = now
    await call.message.edit_text(f"🎁 Ты получил ежедневный бонус!\n💰 {money}, XP {xp}", reply_markup=main_menu())

# ====== Турниры ======
@dp.callback_query(lambda c: c.data=="tournaments")
async def tournaments_menu(call: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for i,t in enumerate(tournaments):
        kb.button(text=f"{t['name']} 🌟", callback_data=f"join_tournament_{i}")
    kb.button(text="Назад в меню", callback_data="menu")
    await call.message.edit_text("Выберите турнир:", reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith("join_tournament_"))
async def join_tournament(call: types.CallbackQuery):
    idx = int(call.data.split("_")[-1])
    t = tournaments[idx]
    user = get_player(call.from_user.id)
    if user["level"]<t["level_req"]:
        await call.message.edit_text("❌ Уровень слишком низкий для участия", reply_markup=main_menu())
        return
    money = t["reward_money"]
    xp = t["reward_xp"]
    user["money"] += money
    user["xp"] += xp
    await call.message.edit_text(f"🏆 Турнир пройден! 💰 {money}, XP {xp}", reply_markup=main_menu())

# ====== Меню ======
@dp.callback_query(lambda c: c.data=="menu")
async def menu(call: types.CallbackQuery):
    await call.message.edit_text("Главное меню:", reply_markup=main_menu())

# ====== Запуск бота ======
if __name__=="__main__":
    print("Mega Football RPG Bot запущен!")
    asyncio.run(dp.start_polling(bot))
