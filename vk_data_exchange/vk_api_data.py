from time import sleep
import vk
from vk_data_exchange.vk_config import vk_user_token, vk_version, vk_host


class VKAPI:

    def __init__(self):
        self.vk_api_session = vk.API(access_token=vk_user_token)
        self.vk_version = vk_version
        self.vk_host = vk_host

    def search_candidates(self, age: int, sex: int, city: str) -> list:
        """
        :param city: city of the candidate
        :param sex: sex of the candidate
        :param age: age of the candidate
        :return: list of candidates
        """

        list_of_candidates = []
        response = self.vk_api_session.users.search(
            v=self.vk_version,
            offset=0,
            count=1000,
            sex=sex,
            age_from=age,
            age_to=age,
            city_id=self.get_city_id(city))

        for candidate in response['items']:
            if not candidate['is_closed'] \
                    or candidate['can_access_closed']:
                list_of_candidates.append({
                    'id': candidate['id'],
                    'first_name': candidate['first_name'],
                    'last_name': candidate['last_name'],
                    'link': f'https://vk.com/id{candidate["id"]}',
                    'photos_ids': self.get_photos_ids(candidate['id'])
                })
                sleep(0.33)

        return list_of_candidates

    def get_photos_ids(self, user_id) -> list:

        result = []
        response = self.vk_api_session.photos.get(
            v=self.vk_version,
            offset=0,
            count=1000,
            album_id='profile',
            extended=1,
            owner_id=user_id,
        )

        photos_to_sort = []
        for item in response['items']:
            photos_to_sort += [{'id': item['id'],
                                'likes': item['likes']['count']
                                }]

        photos_to_sort.sort(key=lambda dictionary: dictionary['likes'],
                            reverse=True)

        for item in photos_to_sort[:3]:
            result += [item['id']]

        return result

    def get_city_id(self, city):

        city_id = 0
        cities = self.vk_api_session.database.getCities(
            v=self.vk_version,
            offset=0,
            count=1000,
            q=city,
            need_all=1
        )
        if cities['count'] > 0:
            city_id = cities['items'][0]['id']
        return city_id
