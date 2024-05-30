# VK chat\-bot "FindMe"
Бот для знакомств, поиск по возрасту, полу и городу

## Требования
* pip install -r requirement.txt
* создать .env-файл для хранения конфиденциальной информации
* получить ключ сообщества 
* получить ключ для приложения

## Пример .env-файла
ACCESS_TOKEN="ytrifihjgv" - ключ сообщества<br> 
ACCESS_TOKEN_API="iuyiuyiu" - ключ приложения<br>
USER_ID="7646534564"<br>
USER_NAME_DB="postgres"<br>
USER_PASSWORD_DB=""

## Схема базы данных
![image](res/scheme_db.png)

## Работа с чатом
![image](res/statechart_diagram.png)
### Начало регистрации
![image](res/registration.jpg)
### Заполнение анкеты
![image](res/questionnaire.jpg)
### Создание параметров для поиска
![image](res/criteria.jpg)
### Главное меню (выполнить поиск, редактировать параметры поиска, переход в список избранных или в черный список)
![image](res/main_menu.jpg)
### Результат поиска (переход к следующей или предыдущей, добавить в вписки, вернуться в главное меню)
![image](res/search.jpg)



