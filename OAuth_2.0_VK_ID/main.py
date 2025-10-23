import hashlib
import base64
import random
import string
import httpx
import asyncio
import json
import uvicorn
from urllib.parse import urlencode
from fastapi import FastAPI, Request, Header, HTTPException
from config_oauth import settings_ssl, settings_token, settings_api

fast_api = FastAPI()

class GeneratePixi():

    def __init__(self):
        self.random_string = ''
        self.encode_base64_url = ''

    def generate_random_string(self, in_out=False) -> str:
        lenght = random.randint(43, 128)
        characters = string.ascii_letters + string.digits + '-_'
        random_string = ''.join(random.choice(characters) for _ in range(lenght))
        if not in_out:
            self.random_string = random_string
            return self.random_string
        else:
            return random_string

    def generate_hash_code(self) -> str:
        code_to_bytes = self.random_string.encode('utf-8')
        sha_256 = hashlib.sha256(code_to_bytes).digest()
        base_64 = base64.urlsafe_b64encode(sha_256).decode('utf-8').rstrip('=')
        self.encode_base64_url = base_64
        return self.encode_base64_url

    # def base_64_url_encode(self) -> str:
    #     encoded = base64.urlsafe_b64encode(self.hash_random_string.encode('utf-8'))
    #     encoded_str = encoded.decode('utf-8')
    #     encoded_str = encoded_str.rstrip('=')
    #     self.encode_base64_url = encoded_str
    #     return self.encode_base64_url
    
    # def base_64_url_decode(self, encoded_string: str) -> str:
    #     if len(encoded_string) % 4 == 0:
    #         decoded = base64.urlsafe_b64code_challengedecode(encoded_string)
    #         decoded_str = decoded.decode('utf-8')


class GetToken:

    get_token_url = 'https://id.vk.ru/oauth2/auth' 
    auth_user_url = 'https://id.vk.ru/authorize'

    ID_CLIENT = settings_token.ID_CLIENT
    REDIR_URL = settings_token.REDIR_URL

    def __init__(self, code=None, state_ans=None, device_id=None ):
        self.code_challenge = ''
        self.state = ''
        self.code_verifier = ''
        self.code = code
        self.state_ans = state_ans
        self.device_id = device_id

    def get_auth_url(self) -> str:
        auth_data = {
        'response_type': 'code',
        'client_id': str(self.ID_CLIENT),
        'redirect_uri': str(self.REDIR_URL),
        'code_challenge': str(self.code_challenge),
        'code_challenge_method': 'S256',
        'state': str(self.state),
        'scope': 'vkid.personal_info'
        }

        auth_data_url = urlencode(auth_data)
        join_auth_url = f'{self.auth_user_url}?{auth_data_url}'
        return join_auth_url


    async def post_user_token(self) -> dict:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'authorization_code',
            'code_verifier': str(self.code_verifier),
            'redirect_uri': str(self.REDIR_URL),
            'code': str(self.code),
            'client_id': str(self.ID_CLIENT),
            'device_id': str(self.device_id),
            'state': str(self.state_ans)}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self.get_token_url,
                headers=headers,
                data=data)
            
        data_response = response.json()
        user_dict = {
            data_response['user_id']: {
                'access_token': data_response['access_token'],
                'refresh_token': data_response['refresh_token']

            }
        }
        return user_dict


pixi = GeneratePixi()
token = GetToken()

def validate_token(token: str) -> bool:
    return token == str(settings_api.KEY)

@fast_api.get('/give_auth')
async def give_auth(key: str = Header(...)) -> dict:
    token_ = key.split(" ")[-1]
    if validate_token(token_):
        token.code_verifier = pixi.generate_random_string()
        token.state = pixi.generate_random_string(in_out=True)
        token.code_challenge = pixi.generate_hash_code()
        data = token.get_auth_url()
        answer = {'url_auth': str(data)}
        return answer
    else:
        raise HTTPException(status_code=401, detail="Invalid token")

@fast_api.get('/callback')
async def vk_callbacl(requests: Request):
    code = requests.query_params.get('code')
    state_ans = requests.query_params.get('state')
    device_id = requests.query_params.get('device_id')
    token.code = code
    token.state_ans = state_ans
    token.device_id = device_id
    return {'code': token.code, 'state_ans': token.state_ans, 'device_id': token.device_id}

@fast_api.get('/give_token')
async def give_token(key: str = Header(...)) -> dict:
    token_ = key.split(" ")[-1]
    if validate_token(token_):
        dict_ = await token.post_user_token()
        return dict_
    else:
        raise HTTPException(status_code=401, detail="Invalid token")

if __name__ == '__main__':

    KEYFILE = settings_ssl.SSL_KEYFILE
    CERTFILE = settings_ssl.SSL_CERTFILE

    uvicorn.run("test:fast_api", host="0.0.0.0", port=443, ssl_keyfile=KEYFILE, ssl_certfile=CERTFILE, reload=True)