import requests
import os


def download_new_version(file_name: str, url: str):
    # Faz o download do arquivo
    response = requests.get(url)
    # Verifica se o download foi bem-sucedido
    if response.status_code == 200:
        # Apaga o antigo arquivo.
        try:
            os.remove(file_name)
        except FileNotFoundError:
            pass

        # Escreve o conteúdo no arquivo local
        with open(file_name, 'wb') as f:
            f.write(response.content)


if __name__ == '__main__':
    try:
        download_new_version('../main.exe', 'https://github.com/LuizGusQueiroz/Automacoes/raw/main/GS/Operacoes%20em%20PDF/_Manipulador%20de%20PDF%20-%20Tess/main.exe')
    except Exception as e:
        print(e)
        input()
