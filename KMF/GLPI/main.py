from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from time import sleep
import pandas as pd
import pyautogui
import os


def main() -> None:
    chamados: pd.DataFrame = get_chamados()
    nav, wait = start_nav()
    run(nav, wait, chamados)


def run(nav, wait, chamados: pd.DataFrame, sleep_time: float = 0.5) -> None:
    for i in range(len(chamados)):
        nav.get(chamados['LINK URL'].iloc[i])
        sleep(2)
        pyautogui.moveTo(0, pyautogui.size()[1] // 2)
        pyautogui.click()
        for column in chamados.columns[1:]:
            # Preenche o campo atual
            pyautogui.press('tab')
            sleep(sleep_time)
            pyautogui.write(chamados[column].iloc[i])
        # Envia o formulário
        pyautogui.press('tab')
        pyautogui.press('enter')
        # Aguarda o envio do formulário.
        url = chamados['LINK URL'].iloc[i]
        while nav.current_url == url:
            sleep(0.1)
    nav.close()


def get_chamados() -> pd.DataFrame:
    # Encontra a planilha de chamados
    files = [file for file in os.listdir() if '.xlsx' in file]
    for file in files:
        df = pd.read_excel(file).fillna('')
        if list(df.columns) == ['LINK URL', 'CLIENTE', 'CENTRO DE CUSTO', 'CÓDIGO', 'COMPETÊNCIA',
                                'DOCUMENTAÇÃO DP', 'DOCUMENTAÇÃO FINANCEIRO CP',
                                'DOCUMENTAÇÃO FINANCEIRO CR', 'DOCUMENTAÇÃO MOP',
                                'DOCUMENTAÇÃO OPERAÇÃO', 'DOCUMENTAÇÃO BENEFÍCIOS']:
            df['COMPETÊNCIA'] = df['COMPETÊNCIA'].apply(lambda x: x.strftime('%m/%Y'))
            return df
    raise Exception('Tabela de chamados não encontrada.')


def start_nav():
    # Inicializa o navegador
    nav = webdriver.Chrome(service=Service())
    wait = WebDriverWait(nav, 30)
    nav.maximize_window()
    return nav, wait


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
