import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

TOKEN_GROUP = "vk1.a.8fVwgUe92-RMCj4iElczZEt5lcX9PoiL14Avv0KKh84-1Mu8rLNeL-4pz-vKdkx1uKk22iAdlPFZpGHzj6s45YggcyY1bkHIz9_7R3G-L3GnPwx_giO8-As58n8yJppAAXrX5UQIDEKwjtHSRLl9GfNbn34fTvR-4tqy2Ro6nN1xuX1aPQW58HSix6FXu6g8PuY1CCRobOhWbyZahVwmRA"
TOKEN_USER = ""
GROUP_ID = 232096614

vk_group_session = vk_api.VkApi(token=TOKEN_GROUP)
vk_group = vk_group_session.get_api()

vk_user_session = vk_api.VkApi(token=TOKEN_USER)
vk_user = vk_user_session.get_api()

longpoll = VkBotLongPoll(vk_group_session, GROUP_ID)

user_states = {}
favorites = {}
def main_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Далее", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("В избранное", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("Избранное", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Стоп", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()
def send_message(user_id, text, attachments=None, keyboard=None):
    params = {
        'user_id': user_id,
        'message': text,
        'random_id': get_random_id()
    }
    if attachments:
        params['attachment'] = ",".join(attachments)
    if keyboard:
        params['keyboard'] = keyboard
    vk_group.messages.send(**params)
def get_user_info(user_id):
    try:
        info = vk_user.users.get(
            user_ids=user_id,
            fields='sex,bdate,city'
        )[0]
        return info
    except Exception as e:
        print(f"[Ошибка get_user_info] {e}")
        return None
def search_users(sex, age_from, age_to, city_id):
    try:
        results = vk_user.users.search(
            count=50,
            fields='city,sex,photo_id',
            sex=sex,
            age_from=age_from,
            age_to=age_to,
            city=city_id,
            has_photo=1,
            status=1,
            sort=0
        )
        return results.get('items', [])
    except Exception as e:
        print(f"[Ошибка search_users] {e}")
        return []
def get_top_photos(user_id):
    try:
        photos = vk_user.photos.get(
            owner_id=user_id,
            album_id='profile',
            extended=1
        )
        sorted_photos = sorted(
            photos['items'],
            key=lambda x: x['likes']['count'],
            reverse=True
        )
        top3 = sorted_photos[:3]
        return [f"photo{p['owner_id']}_{p['id']}" for p in top3]
    except Exception as e:
        print(f"[Ошибка get_top_photos] {e}")
        return []
def show_next_candidate(user_id):
    state = user_states[user_id]
    results = state['results']
    while results:
        candidate = results.pop(0)
        if candidate['id'] not in state['shown_ids']:
            state['shown_ids'].append(candidate['id'])
            photos = get_top_photos(candidate['id'])
            send_message(
                user_id,
                f"{candidate['first_name']} {candidate['last_name']}\nhttps://vk.com/id{candidate['id']}",
                attachments=photos,
                keyboard=main_keyboard()
            )
            return
    info = state['search_params']
    new_results = search_users(
        info['sex'], info['age_from'], info['age_to'], info['city_id']
    )
    new_results = [c for c in new_results if c['id'] not in state['shown_ids']]
    if new_results:
        state['results'] = new_results
        show_next_candidate(user_id)
    else:
        send_message(user_id, "Кандидаты закончились.", keyboard=main_keyboard())
print("✅ Бот запущен...")
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        user_id = event.message['from_id']
        text = event.message.get('text', '').strip().lower()
        if user_id not in user_states:
            user_states[user_id] = {
                'step': 0,
                'results': [],
                'shown_ids': [],
                'search_params': {}
            }
        state = user_states[user_id]
        if text in ['/start', 'привет', 'начать']:
            info = get_user_info(user_id)
            if info:
                sex = 1 if info['sex'] == 2 else 2
                city_id = info.get('city', {}).get('id', None)
                search_params = {
                    'sex': sex,
                    'age_from': 18,
                    'age_to': 35,
                    'city_id': city_id
                }
                state['search_params'] = search_params
                state['shown_ids'] = []
                send_message(user_id, "Ищу кандидатов...", keyboard=main_keyboard())
                results = search_users(**search_params)
                state['results'] = results
                show_next_candidate(user_id)
            else:
                send_message(user_id, "Не удалось получить твои данные.", keyboard=main_keyboard())
        elif text == "далее":
            show_next_candidate(user_id)
        elif text == "в избранное":
            idx_list = state['shown_ids']
            if idx_list:
                last_id = idx_list[-1]
                candidate = vk_user.users.get(user_ids=last_id, fields='first_name,last_name')[0]
                favorites.setdefault(user_id, []).append(candidate)
                send_message(user_id, "Добавил в избранное ✅", keyboard=main_keyboard())
            else:
                send_message(user_id, "Нет кандидата для добавления.", keyboard=main_keyboard())
        elif text == "избранное":
            fav_list = favorites.get(user_id, [])
            if fav_list:
                for cand in fav_list:
                    photos = get_top_photos(cand['id'])
                    send_message(
                        user_id,
                        f"{cand['first_name']} {cand['last_name']}\nhttps://vk.com/id{cand['id']}",
                        attachments=photos,
                        keyboard=main_keyboard()
                    )
            else:
                send_message(user_id, "У тебя пока нет избранных.", keyboard=main_keyboard())
        elif text == "стоп":
            send_message(user_id, "Окей, останавливаюсь 👋", keyboard=None)
        else:
            send_message(user_id, "Выбери действие с кнопок ниже 👇", keyboard=main_keyboard())