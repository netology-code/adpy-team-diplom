import json
from vk_api.utils import get_random_id
from vkbottle.bot import Bot, Message
from vkbottle import CtxStorage, BaseStateGroup, API  # FSM
from vkbottle import Keyboard, KeyboardButtonColor, Text, OpenLink, Location, EMPTY_KEYBOARD  # Keyboards
from config import token_for_bot, token_for_app
from app.registration import VKRegistration
from app.get_info import VkForParsInfo

bot = Bot(token=token_for_bot)
api = API(token=token_for_app)
vk = VkForParsInfo(access_token=token_for_app)
bot.on.vbml_ignore_case = True  # Lower case for all commands


run_keyboard = (
    Keyboard(inline=True)
    .add(Text("Настроить параметры поиска"))
)

sex_keyboard = (
    Keyboard(inline=True)
    .add(Text("Парня"))
    .add(Text("Девушку"))
)

user_keyboard = (
    Keyboard(inline=True)
    .add(Text("Следующий пользователь"), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text("Добавить в избранное"), color=KeyboardButtonColor.POSITIVE)
    .row()
    .add(Text("Изменить параметры поиска"), color=KeyboardButtonColor.POSITIVE)
)


def test(user_id): # она нужна была мне для того, чтобы передавать юзер айди в другой модуль
    id_of_user = user_id
    return str(id_of_user)


def registration(user_id): # функция регистрации, которая будет вызывать модуль регистрации, и получать инфу для базы данныы.
    vk = VKRegistration(access_token=token_for_app, user_id=test(user_id))
    info = vk.users_info() # тут вся инфа по человеку который зарегался в боте, фио айди даже пол указал, но это не обязательно хранить
    url = "https://vk.com/id{}".format(user_id) # это ссылка будет, будет забираться юзер айди и делать из этого полноценную ссылку


@bot.on.message(text="Регистрация")
async def reg_handler(message: Message):
    user = await bot.api.users.get(message.from_id)
    print(user[0].id)
    registration(user[0].id)
    await message.answer('Регистрация завершена', keyboard=run_keyboard)

ctx = CtxStorage()  # Хранилище для FSM


class SetParams(BaseStateGroup):
    SEX = 0
    CITY = 1
    AGE = 2


@bot.on.message(lev="Настроить параметры поиска")
async def run_searching(message: Message):
    await bot.state_dispenser.set(message.peer_id, SetParams.SEX)
    await message.answer('Какого пола людей ищем?', keyboard=sex_keyboard)


@bot.on.message(state=SetParams.SEX)
async def run_searching_sex(message: Message):
    if message.text == 'Парня':
        ctx.set('sex', 2)
    elif message.text == 'Девушку':
        ctx.set('sex', 1)
    else:
        return 'Выбери предложенные варианты'
    await bot.state_dispenser.set(message.peer_id, SetParams.CITY)
    return 'Напиши город в котором будем искать людей'


@bot.on.message(state=SetParams.CITY)
async def run_searching_city(message: Message):
    city = await api.database.get_cities(q=message.text, country_id=1, count=1)
    if city.items:
        for value in city.items:
            ctx.set('city', value.id)
        await bot.state_dispenser.set(message.peer_id, SetParams.AGE)
        return 'Введи возраст который нужно искать'
    else:
        return "Уточните город"


@bot.on.message(state=SetParams.AGE)
async def run_searching_age(message: Message):
    if message.text.isdigit():  # Для мамкиных аферистов, которые вместо int'a пишут (МНЕ ПЯТЬ ЛЕТ)
        vk.users_get_free(sex=ctx.get('sex'), get_city=ctx.get('city'), age_from=int(message.text), bot_people_id=message.from_id)
    else:
        return "Введите возраст цифрами!"  # Разворачиваем мамкиных аферистов и ждём int'а на этом же этапе.
    await message.answer('Настройки сохранены', keyboard=user_keyboard)
    await bot.state_dispenser.delete(message.peer_id)


@bot.on.message(text='Следующий пользователь')
async def info_next_user(message: Message):
    with open(f'{message.from_id}_data.json', 'r', encoding='utf8') as f:
        data = json.load(f)
        for i in data:
            await message.answer(f'ЧЕЛОВЕК НАЙДЕН: {i["first_name"]} {i["last_name"]}. \n {i["link"]}')
            for b in data[0]['photo_id']:
                print(f'photo{i["link"][17::]}_{b}')
                aza = f'photo{i["link"][-16::]}_{b}'
                await bot.api.messages.send(message='ку', random_id=get_random_id(), attachment=aza, peer_id=message.peer_id) # Это не работает
#
# bot.api.photos.get_upload_server()


bot.run_forever()  # Вечной жизни ботам!]
