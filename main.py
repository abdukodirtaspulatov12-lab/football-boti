export default {
async fetch(request, env) {

if (request.method !== "POST") {
return new Response("Football Bot Running ⚽")
}

const update = await request.json()

if (!update.message) {
return new Response("ok")
}

const chat_id = update.message.chat.id
const user_id = update.message.from.id.toString()
const text = update.message.text

let player = await getPlayer(env,user_id)

let answer = ""

if (text === "/start") {

answer =
`⚽ Футбольная игра

Команды:
/profile
/match
/train
/chest
/tournament
/buy
/team
/stadium
/daily
/top`

}

else if (text === "/profile") {

const power = calculatePower(player)

answer =
`👤 Профиль

💰 Монеты: ${player.coins}
⚡ Сила: ${power}
🏟 Стадион: ${player.stadium}`

}

else if (text === "/match") {

const power = calculatePower(player)

const winChance = 40 + power * 4
const r = Math.floor(Math.random()*100)

if (r <= winChance) {

const reward = random(40,100)

player.coins += reward

answer = `🏆 Победа!\n+${reward} монет`

} else {

answer = "❌ Поражение"

}

}

else if (text === "/train") {

const now = Date.now()

if (now - player.last_train < 600000) {

answer = "⏳ Тренировка через 10 минут"

} else {

if (player.coins < 30) {

answer = "❌ Нужно 30 монет"

} else {

player.coins -= 30

const pos = randomPosition()

player.team[pos]++

player.last_train = now

answer = `🏋️ Тренировка\nИгрок улучшил: ${pos}`

}

}

}

else if (text === "/chest") {

const r = Math.random()

let reward

if (r < 0.6) {

reward = random(20,50)
answer = `📦 Обычный сундук\n+${reward} монет`

}
else if (r < 0.9) {

reward = random(50,120)
answer = `💎 Редкий сундук\n+${reward} монет`

}
else {

reward = random(120,250)
answer = `👑 Легендарный сундук\n+${reward} монет`

}

player.coins += reward

}

else if (text === "/tournament") {

if (player.coins < 80) {

answer = "❌ Нужно 80 монет"

} else {

player.coins -= 80

const wins = random(0,3)

const reward = wins * 100

player.coins += reward

answer =
`🏆 Турнир

Побед: ${wins}
Награда: ${reward}`

}

}

else if (text === "/buy") {

if (player.coins < 120) {

answer = "❌ Нужно 120 монет"

} else {

player.coins -= 120

const pos = randomPosition()

player.team[pos]++

answer = `⚽ Новый игрок: ${pos}`

}

}

else if (text === "/team") {

answer =
`👥 Команда

⚽ Нападающие: ${player.team.striker}
🎯 Полузащитники: ${player.team.midfielder}
🛡 Защитники: ${player.team.defender}
🧤 Вратари: ${player.team.goalkeeper}`

}

else if (text === "/stadium") {

const cost = player.stadium * 200

if (player.coins < cost) {

answer = `❌ Нужно ${cost} монет`

} else {

player.coins -= cost

player.stadium++

answer = `🏟 Стадион уровень ${player.stadium}`

}

}

else if (text === "/daily") {

const now = Date.now()

if (now - player.last_daily < 86400000) {

answer = "⏳ Бонус уже получен"

} else {

const reward = random(100,200)

player.coins += reward
player.last_daily = now

answer = `🎁 Бонус +${reward} монет`

}

}

else if (text === "/top") {

answer = "🏆 Топ игроков пока недоступен"

}

await env.PLAYERS.put(user_id,JSON.stringify(player))

await send(chat_id,answer,env)

return new Response("ok")

}
}


async function getPlayer(env,id){

let p = await env.PLAYERS.get(id)

if(!p){

return {
coins:200,
stadium:1,
last_train:0,
last_daily:0,
team:{
striker:1,
midfielder:1,
defender:1,
goalkeeper:1
}
}

}

return JSON.parse(p)

}


function calculatePower(player){

return (
player.team.striker*2 +
player.team.midfielder*2 +
player.team.defender*2 +
player.team.goalkeeper*2 +
player.stadium
)

}


function random(min,max){

return Math.floor(Math.random()*(max-min+1))+min

}

function randomPosition(){

const p = ["striker","midfielder","defender","goalkeeper"]

return p[Math.floor(Math.random()*p.length)]

}


async function send(chat,text,env){

await fetch(
`https://api.telegram.org/bot${env.BOT_TOKEN}/sendMessage`,
{
method:"POST",
headers:{ "Content-Type":"application/json" },
body:JSON.stringify({
chat_id:chat,
text:text
})
}
)

}
