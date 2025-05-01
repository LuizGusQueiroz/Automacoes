from os import listdir, path, mkdir, rename, getcwd, remove
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import *
from selenium import webdriver
from PyPDF2 import PdfReader
from zipfile import ZipFile
from time import sleep
import requests

# Inicializa o navegador
service = Service()

options = Options()
options.add_experimental_option("prefs", {
    "download.default_directory": getcwd(),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})


nav = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(nav, 30)


def espera_aparecer(xpath: str, n: int = 20) -> None:
    """
    Espera n segundos até que determinado item esteja na tela.
    :param xpath: Uma string com o xpath do item que se deseja esperar aperecer.
    :param n: O total de segundos que se deseja esperar.
    """
    for _ in range(n):
        if nav.find_elements('xpath', xpath):
            wait.until(EC.element_to_be_clickable(('xpath', xpath)))
            return
        sleep(1)
    raise NoSuchElementException(f'{xpath} não encontrado em {n} segundos de espera')


def interact(action: str, xpath: str, keys: str = None, n_tries: int = 10) -> None:
    """
    Interage com determinado elemento na tela.
    Primeiro chama a função 'espera_aparecer' para não causar erro de Not Found.
    :param xpath: Uma string com o xpath do elemento que se deseja esperar aperecer.
    """
    actions = ['click', 'write', 'clear']
    if action not in actions:
        raise TypeError(f'{action} must be in {actions}')
    try:
        espera_aparecer(xpath)
    except NoSuchElementException:
        print(xpath)
    for try_i in range(n_tries):
        try:
            # Find the element
            element = nav.find_element('xpath', xpath)
            # Choose the right action to do
            if action == 'click':
                element.click()
            elif action == 'write':
                element.send_keys(keys)
            elif action == 'clear':
                element.clear()
            return
        except (NoSuchElementException or ElementNotInteractableException or
                ElementClickInterceptedException or StaleElementReferenceException):
            sleep(1)
        except UnexpectedAlertPresentException:
            try:
                alert = nav.switch_to.alert
                alert.dismiss()  # Recusa o alerta
            except NoAlertPresentException:
                pass


# Lê as credenciais de acesso
with open('config.txt', 'r') as file:
    # Separa o arquivo por linha
    dados = file.read().split('\n')
    # Separa cada chave do seu valor
    dados = [(linha.split('-->')[0], linha.split('-->')[1].strip()) for linha in dados]
    # Cria um dicionário com os valores lidos
    dados = {chave: valor for chave, valor in dados}

def run():
    # Acessa o site da prefeitura
    nav.get('https://nfse.salvador.ba.gov.br/')
    # Preenche as credenciais
    interact('write', '//*[@id="txtLogin"]', dados['LOGIN'])
    interact('write', '//*[@id="txtSenha"]', dados['SENHA'])
    while nav.find_elements('xpath', '//*[@id="cmdLogin"]'):
        interact('write', '//*[@id="tbCaptcha"]', '')
        sleep(1)

    espera_aparecer('//*[@id="menu-lateral"]/li[4]/a', 50)
    # Clica em 'Consultar NFS-e'
    interact('click', '//*[@id="menu-lateral"]/li[4]/a')
    # Escolhe a competência desejada.
    Select(nav.find_element('xpath', '//*[@id="ddlMes"]')).select_by_visible_text(dados['Competencia'])
    # Clica em 'NFS-e Emitidas'
    interact('click', '//*[@id="btEmitidas"]')
    # Guarda a referência da janela principal
    main_window = nav.current_window_handle
    # Encontrar o identificador da nova janela aberta.
    for window in nav.window_handles:
        if window != main_window:
            sec_window = window
            nav.switch_to.window(sec_window)
            break

    # Acessa os dados da tabela de notas
    notas = nav.find_element('xpath', '//*[@id="dgNotas"]').text.split('\n')[2:-1]
    # Pega nota sim, nota não, pois as informações de cada nota estão divididas em duas linhas,
    # mas a segunda linha não tem informações necessárias para esta aplicação.
    notas = [nota for i, nota in enumerate(notas) if i % 2 == 0]
    for i, row in enumerate(notas):
        print([row])
        interact('click', f'//*[@id="dgNotas"]/tbody/tr[{i+2}]/td[1]/a')
        # É aberta uma tela na janela principal
        # Encontrar o identificador da nova janela.
        for window in nav.window_handles:
            if window not in [main_window, sec_window]:
                nav.switch_to.window(window)
                break

        img_element = WebDriverWait(nav, 10).until(
            EC.presence_of_element_located(('xpath', '//*[@id="img"]'))
        )
        # Capturar o URL da imagem
        img_url = img_element.get_attribute('src')
        # Fazer o download da imagem usando requests
        img_response = requests.get(img_url)
        # Caminho para salvar a imagem
        img_path = 'imagem.jpg'
        # Escrever a imagem no arquivo
        with open(img_path, 'wb') as file:
            file.write(img_response.content)

        break

run()
sleep(100)
