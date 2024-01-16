import vk_api
from pprint import pprint


class VKBotAPI:
    def __init__(self, api_token: str, hometown: str, age: int, sex: int):
        self.api_token = api_token
        self.hometown = hometown
        self.age = age
        self.sex = sex
        self.user_init_link = "https://vk.com/id"

    def api_initiate(self):
        _session = vk_api.VkApi(token=self.api_token)
        return _session

    def get_user_info(self):
        user_search_res = self.api_initiate().method(
            "users.search",
            {
                "hometown": self.hometown,
                "sex": self.sex,
                "age": self.age,
                "has_photo": 1,
            },
        )

        users_links = []
        for usr_lnk in user_search_res["items"]:
            users_links.append(self.user_init_link + str(usr_lnk["id"]))

        user_pics = self.api_initiate().method(
            "photos.getAll", {"owner_id": 831751992, "extended": True}
        )
        cnt = []
        for pic in user_pics["items"]:
            max_likes = str(pic["likes"]["count"])
            cnt.append(int(max_likes))
        cnt = sorted(cnt)[-3:]
        pprint(cnt)

        return user_search_res
