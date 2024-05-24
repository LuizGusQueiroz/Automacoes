import json

logins = {
    'folder': {
        'user1': '123',
        'user2': 'abc'
        },
    'folder2': {
        'user1': '123'
    }
}

file_name = "logins.json"

with open(file_name, 'w', encoding='utf-8') as json_file:
    json.dump(logins, json_file, ensure_ascii=False, indent=4)

