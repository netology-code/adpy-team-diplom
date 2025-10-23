import asyncio
import httpx

from config import auth_settings

class Authentication():

    url = auth_settings.AUTH_URL

    def __init__(self):
        self.auth_api_token = auth_settings.AUTH_TOKEN
        self.headers = {
            'key': self.auth_api_token
        }

    async def give_url_auth(self) -> dict:
        async with httpx.AsyncClient() as client:
            url = self.url + '/give_auth'
            result = await client.get(url=url, headers=self.headers)
            auth_url = result.json()
            return auth_url
        
    async def give_user_token(self, sleep=10) -> dict:
        await asyncio.sleep(sleep)
        async with httpx.AsyncClient() as client:
            url = self.url + '/give_token'
            count_try = 0
            while count_try < 3:
                try:
                    result = await client.get(url=url, headers=self.headers)
                    token_dict = result.json()
                    return token_dict
                except Exception as e:
                    print(e)
                    count_try += 1
