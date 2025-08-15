import os
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from dotenv import load_dotenv
from datetime import datetime

from db import (
    create_user,
    add_candidate,
    add_to_favorites,
    get_favorites,
    add_to_blacklist,
    get_blacklist,
    get_user,
)

load_dotenv()

# ---------------- Токены и ID группы ----------------
TOKEN_GROUP = os.getenv("TOKEN_GROUP")
TOKEN_USER = os.getenv("TOKEN_USER")
GROUP_ID = int(os.getenv("GROUP_ID"))

# ---------------- Сессии VK ----------------
vk_group_session = vk_api.VkApi(token=TOKEN_GROUP)
vk_group = vk_group_session.get_api()

vk_user_session = vk_api.VkApi(token=TOKEN_USER)
vk_user = vk_user_session.get_api()

longpoll = VkBotLongPoll(vk_group_session, GROUP_ID)


# ---------------- Функция для вычисления возраста ----------------
def calculate_age(bdate_str):
    try:
        if bdate_str and len(bdate_str.split(".")) == 3:
            day, month, year = map(int, bdate_str.split("."))
            today = datetime.today()
            age = today.year - year - ((today.month, today.day) < (month, day))
            return age
    except Exception:
        pass
    return None


# ---------------- Состояние пользователей ----------------
user_states = {}


# ---------------- Клавиатуры ----------------
def start_keyboard():
    """Клавиатура только с кнопкой Начать"""
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Начать", color=VkKeyboardColor.POSITIVE)
    return keyboard.get_keyboard()


def main_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Далее", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("В избранное", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("Избранное", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("В чёрный список", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button("Помощь", color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()


# ---------------- Отправка сообщений ----------------
def send_message(user_id, text, attachments=None, keyboard=None):
    params = {"user_id": user_id, "message": text, "random_id": get_random_id()}
    if attachments:
        params["attachment"] = ",".join(attachments)
    if keyboard:
        params["keyboard"] = keyboard
    vk_group.messages.send(**params)


# ---------------- Получение информации о пользователе ----------------
def get_user_info(user_id):
    try:
        info = vk_user.users.get(user_ids=user_id, fields="sex,bdate,city")[0]
        return info
    except Exception as e:
        print(f"[Ошибка get_user_info] {e}")
        return None


# ---------------- Поиск кандидатов ----------------
def search_users(sex, age_from, age_to, city_id):
    try:
        results = vk_user.users.search(
            count=50,
            fields="city,sex,photo_id,bdate",
            sex=sex,
            age_from=age_from,
            age_to=age_to,
            city=city_id,
            has_photo=1,
            status=1,
            sort=0,
        )
        return results.get("items", [])
    except Exception as e:
        print(f"[Ошибка search_users] {e}")
        return []


# ---------------- Получение топ-3 фото ----------------
def get_top_photos(user_id):
    try:
        photos = vk_user.photos.get(owner_id=user_id, album_id="profile", extended=1)
        sorted_photos = sorted(
            photos["items"], key=lambda x: x["likes"]["count"], reverse=True
        )
        top3 = sorted_photos[:3]
        return [f"photo{p['owner_id']}_{p['id']}" for p in top3]
    except Exception as e:
        print(f"[Ошибка get_top_photos] {e}")
        return []


# ---------------- Показ следующего кандидата ----------------
def show_next_candidate(user_id):
    state = user_states[user_id]
    results = state["results"]
    bl_vk_ids = {b.candidate.vk_id for b in get_blacklist(state["user_pk"])}

    while results:
        candidate = results.pop(0)
        if (
            candidate["id"] not in state["shown_ids"]
            and candidate["id"] not in bl_vk_ids
        ):
            state["shown_ids"].append(candidate["id"])
            age = calculate_age(candidate.get("bdate"))

            add_candidate(
                user_id=state["user_pk"],
                vk_id=candidate["id"],
                first_name=candidate["first_name"],
                last_name=candidate["last_name"],
                city=candidate.get("city", {}).get("title"),
                age=age,
                gender=candidate.get("sex"),
            )
            photos = get_top_photos(candidate["id"])
            send_message(
                user_id,
                f"{candidate['first_name']} {candidate['last_name']}\nhttps://vk.com/id{candidate['id']}",
                attachments=photos,
                keyboard=main_keyboard(),
            )
            return

    info = state["search_params"]
    new_results = search_users(
        info["sex"], info["age_from"], info["age_to"], info["city_id"]
    )
    new_results = [
        c
        for c in new_results
        if c["id"] not in state["shown_ids"] and c["id"] not in bl_vk_ids
    ]
    if new_results:
        state["results"] = new_results
        show_next_candidate(user_id)
    else:
        send_message(user_id, "Кандидаты закончились.", keyboard=main_keyboard())


# ---------------- Основной цикл ----------------
print("Бот запущен")

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        user_id = event.message["from_id"]
        text = event.message.get("text", "").strip().lower()

        if user_id not in user_states:
            user = get_user(user_id)
            if not user:
                info = get_user_info(user_id)
                if info:
                    user = create_user(
                        vk_id=user_id,
                        first_name=info["first_name"],
                        last_name=info["last_name"],
                        city=info.get("city", {}).get("title"),
                        age=calculate_age(info.get("bdate")),
                        gender=info.get("sex"),
                    )
                else:
                    send_message(
                        user_id, "Не удалось получить твои данные.", keyboard=start_keyboard()
                    )
                    continue

            user_states[user_id] = {
                "step": 0,   # 0 = старт, 1 = поиск идёт
                "results": [],
                "shown_ids": [],
                "search_params": {},
                "user_pk": user.id,
            }

        state = user_states[user_id]

        # ---------------- Команда /start ----------------
        if text in ["/start", "привет"] and state["step"] == 0:
            send_message(
                user_id,
                """Привет! Я помогу найти интересных людей для знакомств 🎯

        Вот что я умею:
        - "Далее" — показать следующего кандидата
        - "В избранное" — добавить кандидата в свой список
        - "Избранное" — показать список избранных
        - "В чёрный список" — скрыть кандидата
        - "Помощь" — вывести список всех команд

        Нажми "Начать", чтобы запустить поиск 👇""",
                keyboard=start_keyboard(),
            )

        elif text == "начать" and state["step"] == 0:
            info = get_user_info(user_id)
            if info:
                sex = 1 if info["sex"] == 2 else 2
                city_id = info.get("city", {}).get("id", None)
                state["search_params"] = {
                    "sex": sex,
                    "age_from": 18,
                    "age_to": 35,
                    "city_id": city_id,
                }
                state["shown_ids"] = []
                state["step"] = 1  # переключаем в режим поиска

                send_message(user_id, "Ищу кандидатов...", keyboard=main_keyboard())
                state["results"] = search_users(**state["search_params"])
                show_next_candidate(user_id)
            else:
                send_message(user_id, "Не удалось получить твои данные.", keyboard=start_keyboard())

        # ---------------- Кнопка "Далее" ----------------
        elif text == "далее" and state["step"] == 1:
            show_next_candidate(user_id)

        # ---------------- Кнопка "В избранное" ----------------
        elif text == "в избранное" and state["step"] == 1:
            if state["shown_ids"]:
                last_id = state["shown_ids"][-1]
                add_to_favorites(state["user_pk"], last_id)
                send_message(user_id, "Добавил в избранное", keyboard=main_keyboard())
            else:
                send_message(user_id, "Нет кандидата для добавления.", keyboard=main_keyboard())

        # ---------------- Кнопка "Избранное" ----------------
        elif text == "избранное" and state["step"] == 1:
            fav_list = get_favorites(state["user_pk"])
            if fav_list:
                for fav in fav_list:
                    candidate = fav.candidate
                    photos = get_top_photos(candidate.vk_id)
                    send_message(
                        user_id,
                        f"{candidate.first_name} {candidate.last_name}\nhttps://vk.com/id{candidate.vk_id}",
                        attachments=photos,
                        keyboard=main_keyboard(),
                    )
            else:
                send_message(user_id, "У тебя пока нет избранных.", keyboard=main_keyboard())

        # ---------------- Кнопка "В чёрный список" ----------------
        elif text == "в чёрный список" and state["step"] == 1:
            if state["shown_ids"]:
                last_vk_id = state["shown_ids"][-1]
                add_to_blacklist(state["user_pk"], last_vk_id)
                send_message(user_id, "Добавил в чёрный список", keyboard=main_keyboard())
                show_next_candidate(user_id)
            else:
                send_message(user_id, "Нет кандидата для добавления в чёрный список.", keyboard=main_keyboard())

        # ---------------- Кнопка "Помощь" ----------------
        elif text == "помощь":
            send_message(
                user_id,
                """Доступные команды:
Далее — следующий кандидат
В избранное — добавить кандидата
Избранное — список избранных
В чёрный список — скрыть кандидата
""",
                keyboard=main_keyboard() if state["step"] == 1 else start_keyboard(),
            )

        # ---------------- Неизвестная команда ----------------
        else:
            send_message(
                user_id,
                "Выбери действие с кнопок ниже",
                keyboard=main_keyboard() if state["step"] == 1 else start_keyboard(),
            )