from vkbottle import BaseStateGroup, CtxStorage
from vkbottle.bot import Bot, Message
from vkbottle.api import API
from config import bot_settings
from src.authentication.authentication import Authentication

bot = Bot(bot_settings.BOT_TOKEN)
ctx = CtxStorage()

users = {}

class Reg(BaseStateGroup):
    URL = 0
    TOKEN = 1

@bot.on.message(text="/reg")
async def reg_handler(message: Message):
    await bot.state_dispenser.set(message.peer_id, Reg.URL)
    await message.answer('Ок, вам будет прислан url для авторизации')

@bot.on.message(state=Reg.URL)
async def url_handler(message: Message):
    auth = Authentication()
    url_auth = await auth.give_url_auth()
    await bot.state_dispenser.set(message.peer_id, Reg.TOKEN)
    await message.answer(url_auth)

@bot.on.message(state=Reg.TOKEN)
async def token_handler(message: Message):
    user_id = message.from_id
    auth = Authentication()
    token = await auth.give_user_token()
    ctx.set('token', token)
    await bot.state_dispenser.delete(message.peer_id)
    users[user_id] = token #json key - refresh_token, access_token, id_token, token_type, expires_in, user_id, state, scope  

@bot.on.message(text="поиск")
async def search_user(message):
    user_id = message.from_id
    token = users[user_id]['access_token']
    print(token)
    user_api = API(token)
    result = await user_api.users.search(
        q="Иван Иванов",  # строка поиска
        city=1,           # ID города (1 — Москва)
        age_from=18,
        age_to=30,
        count=5,          # количество результатов
        fields="city,domain"
    )
    text = "\n".join([f"{u.first_name} {u.last_name} — vk.com/{u.domain}" for u in result.items])
    await message.answer(f"Найденные пользователи:\n{text}")


bot.run_forever()
