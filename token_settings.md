# Как создать себе ACCESS_TOKEN

1. Вы должны быть авторизованы в VK<br>
2. Открываем ссылку https://dev.vk.com/ru<br>
3. Далее переходим в меню "Приложения".
4. Нажимаем на кнопку "Создать приложение"<br>
<img width="1280" height="738" alt="image" src="https://github.com/user-attachments/assets/48bf7a0c-9af7-480f-8139-72f55548574c" />
5. Придумываем название и нажимаем "Создать"<br>
<img width="1244" height="768" alt="image" src="https://github.com/user-attachments/assets/5bdae13e-c19b-4ec7-865a-47570be3ae84" />
6. Слева переходим в меню "Размещение"<br>

7. Указываем ссылку https://oauth.vk.com/blank.html в блоке "Десктопная версия сайта" и "Режим разработки" после этого нажимаем "Сохранить".
<img width="1029" height="659" alt="image" src="https://github.com/user-attachments/assets/ed043081-fddc-4f5f-bb0e-24df8fc01c8f" />
8. В блоке справа запоминаем ID приложения<br>

<img width="349" height="166" alt="image" src="https://github.com/user-attachments/assets/fb15aaf5-89ac-402c-ac2f-2acf32dd422c" />  
<br>
10. Меняем {client_id} на ID приложения(п.8) в ссылке<br>
https://oauth.vk.com/authorize?client_id={client_id}&display=page&scope=friends,photos&response_type=token&v=5.199&state=123456&redirect_uri=https://oauth.vk.com/blank.html

11. Вставляем ссылку в браузер и нажимаем Enter
12. Нажимаем "Разрешить"
13. В браузерной строке появится новая ссылка https://oauth.vk.com/blank.html#access_token={TOKEN}&expires_in=86400&user_id=171691064&state=123456
где {TOKEN} - Ваш токен.  

14. Чтобы проверить его работоспособность нужно взять код ниже и запустить его с Вашим токеном и id 
```python
import requests


class VK:

   def __init__(self, access_token, user_id, version='5.199'):
       self.token = access_token
       self.id = user_id
       self.version = version
       self.params = {'access_token': self.token, 'v': self.version}


   def users_info(self):
       url = 'https://api.vk.com/method/users.get'
       params = {'user_ids': self.id}
       response = requests.get(url, params={**self.params, **params})
       return response.json()

access_token = 'access_token'
user_id = 'user_id'
vk = VK(access_token, user_id)

print(vk.users_info())
```


