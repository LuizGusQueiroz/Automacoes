from os import listdir, path, mkdir, rename, getcwd, remove
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium import webdriver
from datetime import datetime
from PyPDF2 import PdfReader
from time import sleep

dir = f'{getcwd()}\\notas'
# Inicializa o navegador
service = Service(ChromeDriverManager().install())
options = Options()
options.add_experimental_option("prefs", {
    "download.default_directory": dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True,
    "profile.default_content_setting_values.automatic_downloads": 1
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
        print('NoSuchElement: ', xpath)
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
        except NoSuchElementException:
            sleep(1)
        except ElementNotInteractableException:
            sleep(1)
        except ElementClickInterceptedException:
            sleep(1)
        except StaleElementReferenceException:
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
    # Converte a data no modelo dd/mm/YYYY para uma variável do tipo datetime
    dia = datetime(int(dados['Data'][6:]), int(dados['Data'][3:5]), int(dados['Data'][:2]))


def run():
    if not path.exists(dir):
        mkdir(dir)
    # Vai para o site do ISS Fortaleza
    nav.get('https://isscuritiba.curitiba.pr.gov.br/iss/default.aspx')
    # Aguarda o site carregar
    sleep(3)
    main_window = nav.current_window_handle

    # Encontrar o identificador da nova janela.
    for window in nav.window_handles:
        if window != main_window:
            nav.switch_to.window(window)
            break

    while nav.find_elements('xpath', '//*[@id="btnLogar"]'):
        interact('clear', '//*[@id="txtLogin"]')
        interact('write', '//*[@id="txtLogin"]', dados['LOGIN'])
        interact('write', '//*[@id="txtSenha"]', dados['SENHA'])
        sleep(7)
        interact('click', '//*[@id="btnLogar"]')
        # Alternar para a nova janela
    sleep(1)

    wait.until(EC.frame_to_be_available_and_switch_to_it(('xpath', '//*[@id="fraMenu"]')))
    # Clica em 'NFS-e'
    interact('click', '//*[@id="td1_div5"]/b/span')

    wait.until(EC.frame_to_be_available_and_switch_to_it(('xpath', '//*[@id="iFrameMenu"]')))
    # Clica em 'Pesquisar NFS-e emitidas/Cancelar NFS-e'
    interact('click', '//*[@id="form1"]/div[2]/table/tbody/tr/td/div[3]/a')
    # Clica em 'Pesquisar'
    interact('click', '//*[@id="btnPesquisar"]')
    # Escolhe a competência desejada.
    Select(nav.find_element('xpath', '//*[@id="Mes"]')).select_by_visible_text(dados['Competencia'])

    sleep(100)



run()
