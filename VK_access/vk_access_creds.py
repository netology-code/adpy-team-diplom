import json

file_path = "/Users/eugene_ivanov/Netology_homeworks/adpy_team_diplom/pythonProject/sensitive.txt"

with open(file_path) as f:
    file = json.loads(f.read())
    vk_token = file["vk_token"]
