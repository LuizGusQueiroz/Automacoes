from os import listdir, getcwd, path, mkdir
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from typing import Tuple
from selenium import webdriver
from PyPDF2 import PdfReader
from time import sleep
import pyautogui

pyautogui.FAILSAFE = False


def inicializa_navegador():
    options = Options()
    options.add_argument("--start-maximized")
    browser = webdriver.Chrome(options=options)
    wait = WebDriverWait(browser, 30)

    return browser, wait


def get_parametros():
    with open('config.txt', 'r') as file:
        parametros = {chave: valor.strip() for chave, valor in
                      [row.split(':') for row in file.read().split('\n')]}
    return parametros


def espera_aparecer(browser, wait, xpath: str, n: int = 20) -> None:
    """
    Espera n segundos até que determinado item esteja na tela.
    :param xpath: Uma string com o xpath do item que se deseja esperar aperecer.
    :param n: O total de segundos que se deseja esperar.
    """
    for _ in range(n):
        try:
            if browser.find_elements('xpath', xpath):
                wait.until(EC.element_to_be_clickable(('xpath', xpath)))
                return
            sleep(1)
        except StaleElementReferenceException:
            sleep(1)
    raise NoSuchElementException(f'{xpath} não encontrado em {n} segundos de espera')


def _interact(browser, wait, action: str, xpath: str, keys: str = None, n_tries: int = 10) -> None:
    """
    Interage com determinado elemento na tela.
    Primeiro chama a função 'espera_aparecer' para não causar erro de Not Found.
    :param xpath: Uma string com o xpath do elemento que se deseja esperar aperecer.
    """
    actions = ['click', 'write', 'clear']
    if action not in actions:
        raise TypeError(f'{action} must be in {actions}')
    try:
        espera_aparecer(browser, wait, xpath)
    except NoSuchElementException:
        raise Exception(f'Elemento nao encontrado: {xpath}')
    for try_i in range(n_tries):
        try:
            # Find the element
            element = browser.find_element(By.XPATH, xpath)
            # Choose the right action to do
            if action == 'click':
                element.click()
            elif action == 'write':
                element.send_keys(keys)
            elif action == 'clear':
                element.clear()
            return
        except NoSuchElementException:
            sleep(1)
        except ElementNotInteractableException:
            sleep(1)
        except StaleElementReferenceException:
            sleep(1)
        except ElementClickInterceptedException:
            sleep(1)
        except UnexpectedAlertPresentException:
            try:
                alert = browser.switch_to.alert
                alert.dismiss()  # Recusa o alerta
            except NoAlertPresentException:
                pass


def js_write(browser, xpath: str, keys: str, n_tries: int = 10) -> None:
    for _ in range(n_tries):
        try:
            browser.execute_script(f"arguments[0].value = '{keys}';", browser.find_element(By.XPATH, xpath))
            return
        except Exception as e:
            sleep(1)


def read_contracheque(path: str) -> str:
    with open(f'Contracheques/{path}', 'rb') as file:
        rows = PdfReader(file).pages[0].extract_text().split('\n')
        nome = ' '.join(rows[11].split()[1:])
        return nome


def main():
    nome_empresa = 'pontodigital'
    template_aviso = 'TESTE {nome}'
    template_mensagem = 'Contracheque {nome}'
    primeira_iteracao = True
    # Cria a pasta de contracheques.
    if not path.exists('Contracheques'):
        mkdir('Contracheques')

    parametros = get_parametros()

    browser, wait = inicializa_navegador()

    def interact(action: str, xpath: str, keys: str = None, n_tries: int = 10) -> None:
        _interact(browser, wait, action, xpath, keys, n_tries)

    browser.get('https://app.nexti.com/#/login')
    # Preenche o campo 'Empresa'.
    interact('write', '//*[@id="inputDomain"]', nome_empresa)
    # Clica em 'Próximo passo'
    interact('click', '//*[@id="next-step"]')
    # Preenche o campo 'Nome do usuário'.
    interact('write', '//*[@id="inputUsername"]', parametros['usuario'])
    # Preenche o campo 'Senha'.
    interact('write', '//*[@id="inputPassword"]', parametros['senha'])
    # Clica em 'Entrar'.
    interact('click', '//*[@id="app"]/div[1]/div/div/div[2]/div/form/div[2]/button')
    # Clica em 'RH Digital'.
    interact('click', '//*[@id="app"]/div[1]/div[2]/div/nexti-left-menu/nav/ul/li[3]/a/span[2]')
    # Clica em 'Avisos e convocações'.
    interact('click', '//*[@id="app"]/div[1]/div[2]/div/nexti-left-menu/nav/ul/li[3]/ul/li/a/span')
    for contracheque in listdir('Contracheques'):
        nome = read_contracheque(contracheque)
        # Clica em 'Novo aviso / convocação'.
        interact('click', '//*[@id="content"]/div[2]/div[1]/div/div[1]/div[2]/button')
        # Preenche o campo 'Nome do aviso / convocação:'.
        interact('write', '//*[@id="content"]/div[3]/div/div[2]/div/div/div[1]/div/div/div[1]/input',
                 template_aviso.format(nome=nome))
        # Preenche o campo 'Envio em:'.
        js_write(browser, '//*[@id="startDate"]/p/input', parametros['data_envio'])
        sleep(0.1)
        js_write(browser, '//*[@id="startDate"]/p/input', parametros['data_envio'])
        interact('click', '//*[@id="startDate"]/p/input')  # É necessário dar um clique para que a data seja aceita.
        # Preenche o campo 'Finaliza em:'.
        js_write(browser, '//*[@id="endDate"]/p/input', parametros['data_fim'])
        sleep(0.1)
        js_write(browser, '//*[@id="endDate"]/p/input', parametros['data_fim'])
        interact('click', '//*[@id="endDate"]/p/input')  # É necessário dar um clique para que a data seja aceita.
        # Clica em 'Enviar para: Ambos'.
        interact('click', '//*[@id="content"]/div[3]/div/div[2]/div/div/div[1]/div/div/div[4]/div/label[3]')
        # Clica em 'Mostrar na: Ambos'.
        interact('click', '//*[@id="content"]/div[3]/div/div[2]/div/div/div[1]/div/div/div[5]/div/label[3]')
        # Clica em 'Aviso'.
        interact('click', '//*[@id="content"]/div[3]/div/div[2]/div/div/div[1]/div/div/div[6]/div[1]/label/i')
        # Clica em 'Editor Avançado'. (Só é necessário na primeira iteração)
        if primeira_iteracao:
            browser.execute_script("arguments[0].click();", browser.find_element(By.CSS_SELECTOR,
                                                                                 '#content > div.__crud-add.ng-scope > div > div.tab-container > div > div > div.app-content-body.checklist-add > div > div > div:nth-child(8) > div.card > div.card-content > div > div > div > div > div > div > label > input'))
            primeira_iteracao = False
            # Fecha a mensagem de enviar notificações
            interact('click', '//*[@id="pushActionRefuse"]')
        # Escreve a mensagem de envio.
        interact('write', '//*[@id="note"]', template_mensagem.format(nome=nome))
        # Clica em 'Envio do arquivo'.
        element = browser.find_element(By.CLASS_NAME, 'file_input_label')
        element.click()
        # Escolhe o arquivo a ser enviado.
        while element.text == 'Envio do arquivo':
            # Escreve o caminho do arquivo.
            pyautogui.write(f'{getcwd()}\\Contracheques\\{contracheque}')
            sleep(1)  # Aguarda o carregamento.
            pyautogui.press('enter')
            sleep(2)
        # Clica em 'Próximo'.
        interact('click', '//*[@id="content"]/div[3]/div/div[2]/div/div/div[1]/div/div/div[8]/div[3]/div')
        # Clica no símbolo com 4 barras horizontais.
        interact('click', '//*[@id="content"]/div[3]/div/div[2]/ul/div/i[1]')
        # Clica no símbolo de funil.
        interact('click', '//*[@id="content"]/div[3]/div/div[2]/div/div/div[2]/div/div[2]/div[1]/i')
        # ---------------------------
        nome = 'PEDRO PEREIRA'
        # ----------------------------
        # Preenche o campo 'Colaborador'.
        interact('clear', '//*[@id="app"]/div[1]/div/div/div/div[2]/div/form/div[6]/div[1]/autocomplete/div/div[1]/input')
        interact('write',
                 '//*[@id="app"]/div[1]/div/div/div/div[2]/div/form/div[6]/div[1]/autocomplete/div/div[1]/input', nome)
        # Aguarda até a lista ser carregada.
        while not bool(browser.find_elements('xpath',
                                             '//*[@id="app"]/div[1]/div/div/div/div[2]/div/form/div[6]/div[1]/autocomplete/div/div[1]/div[2]/li')):
            sleep(1)
        # Espera até o resultado da consulta por colaborador ser carregada.
        autocomplete_results = []
        while not autocomplete_results:
            sleep(1)
            # Acessa o texto de todos os elementos com a classe 'autocomplete-results'.
            autocomplete_results = [element.text for element in
                                    browser.find_elements(By.CLASS_NAME, 'autocomplete-results')
                                    if element.text]

        if 'Nenhum resultado encontrado' in autocomplete_results:
            # Clica no primeiro X.
            interact('click', '//*[@id="app"]/div[1]/div/div[1]/div/div[1]/div/a')
            # Clica no segundo X.
            interact('click', '//*[@id="content"]/div[3]/div/div[1]/div[2]/a')
            # Segue para o próximo contracheque.
            continue

        # Seleciona o primeiro item da lista.
        interact('click',
                 '//*[@id="app"]/div[1]/div/div/div/div[2]/div/form/div[6]/div[1]/autocomplete/div/div[1]/div[2]/li')
        # Clica em 'Filtrar'.
        interact('click', '//*[@id="app"]/div[1]/div/div/div/div[4]/a[2]')
        # Clica em 'Enviar'.
        interact('click', '//*[@id="content"]/div[3]/div/div[2]/ul/div[2]')
        # Clica em 'Sim'.
        interact('click', '//*[@id="app"]/div[2]/div/div/div/div[3]/div[3]/div[2]')

        print(f'Sucesso {nome} -- {contracheque}')
    sleep(100)


main()
if __name__ == '1__main__':
    try:
        main()
    except Exception as e:
        print(e)
