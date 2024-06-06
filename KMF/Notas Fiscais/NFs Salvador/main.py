from os import listdir, path, mkdir, rename, getcwd, remove
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from PyPDF2 import PdfReader
from zipfile import ZipFile
from time import sleep

# Inicializa o navegador
service = Service(ChromeDriverManager().install())

options = Options()
options.add_experimental_option("prefs", {
    "download.default_directory": getcwd(),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})


nav = webdriver.Chrome(service=service, options=options)


def espera_aparecer(xpath: str, n: int = 20) -> None:
    """
    Espera n segundos até que determinado item esteja na tela.
    :param xpath: Uma string com o xpath do item que se deseja esperar aperecer.
    :param n: O total de segundos que se deseja esperar.
    """
    for _ in range(n):
        if nav.find_elements('xpath', xpath):
            return
        sleep(1)
    raise NoSuchElementException(f'{xpath} não encontrado em {n} segundos de espera')


def clica(xpath: str) -> None:
    """
    Clica em determinado elemento na tela.
    Primeiro chama a função 'espera_aparecer' para não causar erro de Not Found.
    :param xpath: Uma string com o xpath do elemento que se deseja esperar aperecer.
    """
    espera_aparecer(xpath)
    try:
        nav.find_element('xpath', xpath).click()
        return
    except NoSuchElementException:
        print(f'Item com xpath {xpath} não encontrado')
    raise NoSuchElementException()


# Lê as credenciais de acesso
with open('config.txt', 'r') as file:
    # Separa o arquivo por linha
    dados = file.read().split('\n')
    # Separa cada chave do seu valor
    dados = [(linha.split('-->')[0], linha.split('-->')[1].strip()) for linha in dados]
    # Cria um dicionário com os valores lidos
    dados = {chave: valor for chave, valor in dados}

# Acessa o site da prefeitura
nav.get('https://nfse.vitoria.es.gov.br/')
# Preenche as credenciais
nav.find_element('xpath', '//*[@id="login"]').send_keys(dados['EMAIL'])
nav.find_element('xpath', '//*[@id="senha"]').send_keys(dados['SENHA'])
# Clica em 'Acessar'
nav.find_element('xpath', '//*[@id="formEntrada"]/div[2]/span/span/input').click()

# Espera até que a próxima página seja carregada
while not nav.find_elements('xpath', '/html/body/div/div[3]/div/h2'):
    sleep(1)

# Clica em 'Entra no Sistema'
try:
    clica('/html/body/div/div[3]/div/p[3]/a')
except NoSuchElementException:
    # O botão não existe, não é necessário fazer nada
    pass