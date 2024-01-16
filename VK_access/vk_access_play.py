from VK_access.vk_access_creds import vk_token
from VK_access.vk_group_api import VKBotAPI

if __name__ == "__main__":
    vk_inst = VKBotAPI(vk_token, "Череповец", 27, 1)
    vk_inst.get_user_info()
