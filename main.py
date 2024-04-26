import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api import VkUpload
import os
from dotenv import load_dotenv

from VKRepository import VKRepository

load_dotenv()

if __name__ == '__main__':
    vk = VKRepository(access_token=os.getenv(key='ACCESS_TOKEN_API'))
    #result = vk.get_user_first_name(478663876)
    result = vk.get_users_list(criteria_dict='')
    assa = ''
            #repository.add_favorites(item)

    # if os.getenv(key='REALIZATION') == 'SQL':
    #     check_db = CheckDBSQL()
    # else:
    #     check_db = CheckDBORM()
    #
    # if check_db.check_db():
    #     sql_repository = SQLRepository()
    #     #start_chat_bot()

