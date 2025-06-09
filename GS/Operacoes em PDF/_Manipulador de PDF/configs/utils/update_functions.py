import requests


def check_update(VERSION: str):
    last_version = get_last_version()
    if type(last_version) == str:
        if VERSION != get_last_version():
            print('Nova versão disponível!')
            print(
                'Para baixar a nova versão, feche e exclua este arquivo (main.py) e execute o arquivo "download_last_version" dentro da pasta "configs".')
            input('Para continuar utilizando esta versão, pressione Enter')

def get_last_version():
    # Endpoint da API para buscar o histórico de commits de um arquivo específico.
    url = f"https://api.github.com/repos/LuizGusQueiroz/Automacoes/commits"
    # Parâmetros da consulta, para buscar commits de um arquivo específico
    params = {'path': "GS/Operacoes em PDF/_Manipulador de PDF/main.exe"}
    try:
        # Envia a requisição GET para a API do GitHub
        response = requests.get(url, params=params)
        response.raise_for_status()  # Levanta uma exceção se houver um erro na requisição
        # Extrai o JSON da resposta
        commits_data = response.json()
        if commits_data:
            # A mensagem do commit mais recente está no primeiro item da lista
            last_commit = commits_data[0]
            commit_message = last_commit['commit']['message']
            return commit_message
        else:
            return None
    except requests.exceptions.RequestException:
        return None
