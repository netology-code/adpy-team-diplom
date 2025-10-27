from collections import namedtuple

from vkbottle import Keyboard, Text


KEYBOARD = namedtuple(
    "Keyboard",
    ["START", "SEX", "AGE", "CITY", "LOOK"],
)(
    (
        Keyboard(True)
        .add(Text("🔍 Поиск", {"cmd": "search"}))
        .row()
        .add(Text("❤️ Закладки", {"cmd": "favorites"}))
        .row()
        .add(Text("🚫 Скрытые", {"cmd": "blocked"}))
    ),
    (
        Keyboard(True)
        .add(Text("♂️ Мужчина", {"cmd": "set_sex", "sex": 2}))
        .add(Text("♀️ Женщина", {"cmd": "set_sex", "sex": 1}))
        .row()
        .add(Text("🔙 Назад", {"cmd": "start"}))
    ),
    (
        Keyboard(True)
        .add(Text("18-20", {"cmd": "set_age", "min": 18, "max": 20}))
        .add(Text("21-24", {"cmd": "set_age", "min": 21, "max": 24}))
        .add(Text("25-29", {"cmd": "set_age", "min": 25, "max": 29}))
        .row()
        .add(Text("30-35", {"cmd": "set_age", "min": 30, "max": 35}))
        .add(Text("36-42", {"cmd": "set_age", "min": 36, "max": 42}))
        .add(Text("43-50", {"cmd": "set_age", "min": 43, "max": 50}))
        .row()
        .add(Text("51+", {"cmd": "set_age", "min": 51}))
        .row()
        .add(Text("🔙 Назад", {"cmd": "search"}))
    ),
    Keyboard(True).add(Text("🔙 Назад", {"cmd": "set_sex"})),
    (
        Keyboard(True)
        .add(Text("❤️ Лайк", {"cmd": "like"}))
        .add(Text("🔄 Еще фото", {"cmd": "next_photo"}))
        .row()
        .add(Text("🔥 В закладки", {"cmd": "wow"}))
        .add(Text("🚫 Скрыть", {"cmd": "not_interested"}))
        .add(Text("➡️ Дальше", {"cmd": "next_user"}))
        .row()
        .add(Text("🔙 Назад", {"cmd": "set_age"}))
    ),
)
