import requests
# redirect_uri = 'https://oauth.vk.com/blank.html'
def get_access_token():
    url = 'https://oauth.vk.com/authorize?'
    params = {
        'client_id': '51851383',
        'redirect_uri': 'https://oauth.vk.com',
        'display': 'page',
        'score': ['offline', 'messages', 'pages', 'photos', 'friends', 'notify'],
        'response_type': 'token',
        'revoke': '1',
        'v': '5.131'
    }
    response = requests.get(url, params=params)
    return response.url

# def
print(get_access_token())

