from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains

import requests

from time import sleep

# Configurações do Chrome
options = Options()
options.add_argument('--disable-extensions')
options.add_argument('--disable-popup-blocking')
options.add_argument('--disable-infobars')
options.add_argument('--safebrowsing-disable-download-protection')
options.add_argument('--safebrowsing-disable-extension-blacklist')
options.add_argument('--safebrowsing-manual-download-blacklist')
options.add_argument('--start-maximized')
options.add_argument(
     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36")


service = Service(EdgeChromiumDriverManager().install())

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


nav.get('https://det.sit.trabalho.gov.br/login')
# Clica em 'Entrar com GOV.br'.
clica('//*[@id="botao"]')
sleep(13)
# Clica em 'Seu certificado digital'
element = nav.find_element('xpath', '//*[@id="login-certificate"]')
actions = ActionChains(nav)
actions.move_to_element(element)
actions.perform()
sleep(1)
element.click()
sleep(10)
#/html/body/div/div[1]/div/div/div[1]/div[1]/div[1]/h2/span
print(nav.find_elements('xpath', '/html/body/div/div[1]/div/div/div[2]/div[1]/div[3]/div[1]'))


sleep(100)


