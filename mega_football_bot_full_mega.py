# mega_football_bot_full_mega.py
import asyncio
import random
import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

API_TOKEN = "ВАШ_ТОКЕН_ЗДЕСЬ"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ==============================
# DATABASE
# ==============================
conn = sqlite3.connect("mega_football_bot_full_mega.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS players(
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    coins INTEGER DEFAULT 100,
    level INTEGER DEFAULT 1,
    exp INTEGER DEFAULT 0,
    attack INTEGER DEFAULT 10,
    defense INTEGER DEFAULT 10,
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    achievements TEXT DEFAULT '',
    last_daily TEXT DEFAULT ''
)
''')
conn.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS pvp_queue(
    user_id INTEGER PRIMARY KEY,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS tournaments(
    tournament_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    status TEXT DEFAULT 'waiting'
)
''')
conn.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS leaderboard(
    user_id INTEGER PRIMARY KEY,
    wins INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1
)
''')
conn.commit()

# ==============================
# UTILS
# ==============================
def get_player(user_id, username=None):
    cursor.execute("SELECT * FROM players WHERE user_id=?", (user_id,))
    player = cursor.fetchone()
    if player:
        return player
    else:
        cursor.execute("INSERT INTO players(user_id, username) VALUES (?,?)", (user_id, username))
        conn.commit()
        return get_player(user_id, username)

def update_player(user_id, **kwargs):
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values())
    values.append(user_id)
    cursor.execute(f"UPDATE players SET {fields} WHERE user_id=?", values)
    conn.commit()

def add_exp(user_id, amount):
    player = get_player(user_id)
    new_exp = player[4] + amount
    new_level = player[3]
    level_up = False
    while new_exp >= new_level * 50:
        new_exp -= new_level * 50
        new_level += 1
        level_up = True
    update_player(user_id, exp=new_exp, level=new_level)
    return level_up, new_level

def can_claim_daily(user_id):
    player = get_player(user_id)
    last_daily = player[10]
    if last_daily:
        last_time = datetime.strptime(last_daily, "%Y-%m-%d")
        if datetime.now() - last_time < timedelta(days=1):
            return False
    return True

def claim_daily(user_id):
    update_player(user_id, coins=get_player(user_id)[2]+50, last_daily=datetime.now().strftime("%Y-%m-%d"))

# ==============================
# KEYBOARDS
# ==============================
def main_menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⚽ Играть PvE", callback_data="match_pve"))
    kb.add(InlineKeyboardButton("⚔ Играть PvP", callback_data="match_pvp"))
    kb.add(InlineKeyboardButton("🏪 Магазин", callback_data="store"))
    kb.add(InlineKeyboardButton("📊 Профиль", callback_data="profile"))
    kb.add(InlineKeyboardButton("💪 Тренировка", callback_data="train"))
    kb.add(InlineKeyboardButton("🏆 Турниры", callback_data="tournament"))
    kb.add(InlineKeyboardButton("🎁 Ежедневный бонус", callback_data="daily"))
    return kb

def store_menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Атака +5 (50 монет)", callback_data="buy_attack"))
    kb.add(InlineKeyboardButton("Защита +5 (50 монет)", callback_data="buy_defense"))
    kb.add(InlineKeyboardButton("Супер-удар (100 монет)", callback_data="buy_boost"))
    kb.add(InlineKeyboardButton("Скин (100 монет)", callback_data="buy_skin"))
    kb.add(InlineKeyboardButton("Назад", callback_data="back"))
    return kb

# ==============================
# COMMANDS
# ==============================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    get_player(message.from_user.id, message.from_user.username)
    await message.answer(f"Привет, {message.from_user.first_name}! Добро пожаловать в **Mega Football Bot Ultra** ⚽🔥", reply_markup=main_menu())

# ==============================
# CALLBACKS
# ==============================
@dp.callback_query_handler(lambda c: True)
async def callbacks(call: types.CallbackQuery):
    user_id = call.from_user.id
    username = call.from_user.username
    player = get_player(user_id, username)

    # ---------- ПРОФИЛЬ ----------
    if call.data == "profile":
        msg = (
            f"📊 Профиль игрока: {player[1]}\n"
            f"💰 Монеты: {player[2]}\n"
            f"🏆 Уровень: {player[3]} (EXP: {player[4]})\n"
            f"⚔️ Атака: {player[5]}\n"
            f"🛡 Защита: {player[6]}\n"
            f"🎮 Матчей сыграно: {player[7]}\n"
            f"🥇 Побед: {player[8]}\n"
            f"🏅 Достижения: {player[9] if player[9] else 'Нет'}"
        )
        await call.message.edit_text(msg, reply_markup=main_menu())

    # ---------- МАГАЗИН ----------
    elif call.data == "store":
        await call.message.edit_text("🏪 Магазин улучшений:", reply_markup=store_menu())

    elif call.data.startswith("buy_"):
        if call.data == "buy_attack":
            if player[2] >= 50:
                update_player(user_id, coins=player[2]-50, attack=player[5]+5)
                await call.answer("Атака увеличена!", show_alert=True)
            else:
                await call.answer("Недостаточно монет!", show_alert=True)
        elif call.data == "buy_defense":
            if player[2] >= 50:
                update_player(user_id, coins=player[2]-50, defense=player[6]+5)
                await call.answer("Защита увеличена!", show_alert=True)
            else:
                await call.answer("Недостаточно монет!", show_alert=True)
        elif call.data == "buy_boost":
            if player[2] >= 100:
                update_player(user_id, coins=player[2]-100, attack=player[5]+10)
                await call.answer("Супер-удар куплен!", show_alert=True)
            else:
                await call.answer("Недостаточно монет!", show_alert=True)
        elif call.data == "buy_skin":
            if player[2] >= 100:
                update_player(user_id, coins=player[2]-100)
                await call.answer("Скин куплен!", show_alert=True)
            else:
                await call.answer("Недостаточно монет!", show_alert=True)
        await call.message.edit_text("🏪 Магазин улучшений:", reply_markup=store_menu())

    elif call.data == "back":
        await call.message.edit_text("Главное меню:", reply_markup=main_menu())

    # ---------- ТРЕНИРОВКА ----------
    elif call.data == "train":
        gain_attack = random.randint(1, 5)
        gain_defense = random.randint(1, 5)
        gain_coins = random.randint(10, 30)
        update_player(user_id,
                      attack=player[5]+gain_attack,
                      defense=player[6]+gain_defense,
                      coins=player[2]+gain_coins)
        level_up, new_level = add_exp(user_id, random.randint(10, 30))
        msg = f"💪 Тренировка прошла!\n+{gain_attack} Атака\n+{gain_defense} Защита\n+{gain_coins} Монет"
        if level_up:
            msg += f"\n🎉 Поздравляем! Вы достигли уровня {new_level}!"
        await call.answer(msg, show_alert=True)
        await call.message.edit_text("Главное меню:", reply_markup=main_menu())

    # ---------- ЕЖЕДНЕВНЫЙ БОНУС ----------
    elif call.data == "daily":
        if can_claim_daily(user_id):
            claim_daily(user_id)
            await call.answer("🎁 Вы получили 50 монет за ежедневный бонус!", show_alert=True)
        else:
            await call.answer("⏳ Бонус можно получить раз в день!", show_alert=True)
        await call.message.edit_text("Главное меню:", reply_markup=main_menu())

    # ---------- PvE МАТЧ ----------
    elif call.data == "match_pve":
        ai_level = random.randint(max(1, player[3]-1), player[3]+3)
        ai_attack = random.randint(5, 20) + ai_level
        ai_defense = random.randint(5, 20) + ai_level
        player_score = player[5] + random.randint(-5,5)
        ai_score = ai_attack + random.randint(-5,5)
        if player_score > ai_score:
            coins_win = random.randint(20, 50)
            update_player(user_id, coins=player[2]+coins_win, matches_played=player[7]+1, wins=player[8]+1)
            level_up, new_level = add_exp(user_id, random.randint(15, 30))
            msg = f"🎉 Победа PvE!\nВы заработали {coins_win} монет!\nВаш результат: {player_score}\nСоперник ИИ: {ai_score}"
            if level_up:
                msg += f"\n🎉 Вы достигли уровня {new_level}!"
        elif player_score < ai_score:
            update_player(user_id, matches_played=player[7]+1)
            msg = f"❌ Поражение PvE!\nВаш результат: {player_score}\nСоперник ИИ: {ai_score}"
        else:
            update_player(user_id, matches_played=player[7]+1, coins=player[2]+10)
            msg = f"⚖️ Ничья PvE!\nВы получили 10 монет за участие.\nВаш результат: {player_score}\nСоперник ИИ: {ai_score}"
        await call.message.edit_text(msg, reply_markup=main_menu())

# ==============================
# RUN BOT
# ==============================
if __name__ == "__main__":
    print("Mega Football Bot Full Mega запущен!")
    executor.start_polling(dp, skip_updates=True)
