from os import startfile
from json import load

try:
    # Carrega os acessos
    with open('logins.json', 'r', encoding='utf-8') as json_file:
        logins = load(json_file)

    login = input('Login: ')
    password = input('Senha: ')
    folder = input('Pasta: ').replace('/', '\\')

    if logins.get(folder, {' ': None}).get(login) == password:
        startfile(f'Pastas\\{folder}')
    else:
        print('Acesso Negado')
        input()
except Exception as e:
    print(e)
    input()
