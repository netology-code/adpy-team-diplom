import requests
import json


class VK:

    def __init__(self, version='5.131', access_token=None, user_id=None):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def users_photo(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id, 'album_id': 'profile', 'photo_sizes': 0, 'extended': 1, 'rev': 1}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def pars_photo(self, vk):
        likes = 0
        photo_info = {}
        photos_json = []
        sorted_likes = []
        photos_info = vk.users_photo()

        for items in photos_info.values():
            for keys, values in items.items():
                if keys == 'items':
                    for each_photo_info in values:
                        for key, value in each_photo_info.items():
                            if key == 'likes':
                                likes = value.get('count')
                            if key == 'sizes':
                                sorted_pic = (sorted(value, key=lambda d: d['height']))[-5:]
                                photo_info['url'] = sorted_pic[-1].get('url')
                        photo_info['likes'] = likes
                        photos_json.append(photo_info)
                        sorted_likes = sorted(photos_json, key=lambda k: k['likes'])[-3:]
                        photo_info = {}

        with open('list_photos.json', 'w') as f:
            json.dump(sorted_likes, f, sort_keys=True, ensure_ascii=False, indent=2)

        return photos_json
