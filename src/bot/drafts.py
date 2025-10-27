from orjson import loads
from vkbottle import BaseStateGroup, PhotoMessageUploader
from vkbottle.bot import Message

from config import BOT, CTX
from keyboards import KEYBOARD


class State(BaseStateGroup):
    CITY = 1


@BOT.on.message(lev="/start")
@BOT.on.message(payload={"cmd": "start"})
async def start(message: Message):
    user_id = message.from_id

    users = await BOT.api.users.get(user_ids=user_id)
    user = users[0]

    if not DB.get_user(user_id):
        DB.add_user(
            vk_user_id=user_id,
            first_name=user.first_name,
            last_name=user.last_name,
        )

    DB.add_message(user_id, "command", "/start")

    await message.answer("👋", keyboard=KEYBOARD.START)


@BOT.on.message(payload={"cmd": "favorites"})
async def get_favorites(message: Message):
    pass


@BOT.on.message(payload={"cmd": "blocked"})
async def get_blocked_list(message: Message):
    pass


@BOT.on.message(payload={"cmd": "search"})
async def select_sex(message: Message):
    user_id = message.from_id

    DB.add_message(user_id, "button", "search")

    await message.answer("Кого будем искать?", keyboard=KEYBOARD.SEX)


@BOT.on.message(payload_map={"cmd": "set_sex"})
async def select_age(message: Message):
    user_id = message.from_id

    answer = loads(message.payload)
    sex = answer["sex"]

    CTX.set("sex", sex)

    DB.add_message(user_id, "button", f"set_sex: {sex}")

    await message.answer("Возраст?", keyboard=KEYBOARD.AGE)


@BOT.on.message(payload_map={"cmd": "set_age"})
async def select_city(message: Message):
    user_id = message.from_id

    answer = loads(message.payload)
    min_age = answer["min"]
    max_age = answer.get("max", None)

    CTX.set("min_age", min_age)
    CTX.set("max_age", max_age)

    DB.add_message(
        user_id,
        "button",
        f"set_age: {min_age}-{max_age}" if max_age else f"set_age: {min_age}+",
    )

    await BOT.state_dispenser.set(user_id, State.CITY)

    await message.answer("Город?", keyboard=KEYBOARD.CITY)


@BOT.on.message(state=State.CITY)
async def check_city(message: Message):
    user_id = message.from_id

    answer = message.text.capitalize().strip()

    DB.add_message(user_id, "text", f"get_city_name: {answer}")

    cities = await BOT.database.get_cities(
        country_id=1,
        q=answer,
        count=1,
    )

    if cities.items and cities.items[0].title == answer:
        city = {cities.items[0].title: cities.items[0].id}

        CTX.set("city", city)

        DB.add_message(user_id, "check", f"set_city: {city}")

        # поиск

        # заглушка-данные
        first_name = ""
        last_name = ""
        age = 0
        link = ""
        photos = []  # формат неясен

        # заглушка-текст
        text = f"{first_name} {last_name}, {age}\n{link}\n"

        # заглушка-картинка
        photo = await PhotoMessageUploader(BOT.api).upload("pic.jpg")

        await BOT.state_dispenser.delete(user_id)

        await message.answer(text, photo, keyboard=KEYBOARD.LOOK)

    else:
        text = f"Получено: {answer}\n\nГород не найден! Попробуем еще раз:"

        await message.answer(text, keyboard=KEYBOARD.CITY)


@BOT.on.message(payload={"cmd": "like"})
async def like_photo(message: Message):
    pass


@BOT.on.message(payload={"cmd": "next_photo"})
async def next_photo(message: Message):
    pass


@BOT.on.message(payload={"cmd": "wow"})
async def add_to_favorites(message: Message):
    pass


@BOT.on.message(payload={"cmd": "not_interested"})
async def ban_user(message: Message):
    pass


@BOT.on.message(payload={"cmd": "next_user"})
async def next_user(message: Message):
    pass


if __name__ == "__main__":
    BOT.run_forever()
