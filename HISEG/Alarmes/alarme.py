from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from os import rename
import datetime

# Acessa as credenciais de acesso
with open('config.txt', 'r') as file:
    credenciais = file.read().split('\n')
    credenciais = [linha.split('-->') for linha in credenciais]
    credenciais = {chave:valor.strip() for chave, valor in credenciais}

email = credenciais['email']
senha = credenciais['senha']
# Obtém a data atual
data = datetime.date.today()
# Formata a data para DDMMAAAA
data = data.strftime("%d%m%Y")
# Diretório onde de download do arquivo
nome_ant = r'C:\Users\Usuario\Downloads\RelatorioAlarmemensagem.xls'
# Diretório a salvar o arquivo
nome_novo = fr'C:\Users\Usuario\Desktop\Alarmes\Alarme {data}.xls'

service = Service(ChromeDriverManager().install())

nav = webdriver.Chrome(service=service)
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
    raise Exception(f'{xpath} não encontrado em {n} segundos de espera')


def clica(xpath: str) -> None:
    """
    Clica em determinado item na tela.
    Primeiro chama a função 'espera_aparecer' para não causar erro de Not Found.
    :param xpath: Uma string com o xpath do item que se deseja esperar aperecer.
    """
    espera_aparecer(xpath)
    # Espera o item ficar 'clicável'
    wait.until(EC.element_to_be_clickable(('xpath', xpath)))
    try:
        nav.find_element('xpath', xpath).click()
    except Exception as e:
        print(xpath)
        print(e)


def escreve(xpath: str, text: str) -> None:
    """
    Escreve em determinado item na tela.
    Primeiro chama a função 'espera_aparecer' para não causar erro de Not Found.
    :param xpath: Uma string com o xpath do item que se deseja esperar aperecer.
    :param text: Uma string com o texto que será escrito no item.
    """
    espera_aparecer(xpath)
    # Espera o item ficar 'clicável'
    wait.until(EC.element_to_be_clickable(('xpath', xpath)))
    try:
        nav.find_element('xpath', xpath).send_keys(text)
    except Exception as e:
        print(xpath)
        print(e)


def seleciona(xpath: str, opcao: str) -> None:
    """
    Seleciona um item em determinado item na tela.
    Primeiro chama a função 'espera_aparecer' para não causar erro de Not Found.
    :param xpath: Uma string com o xpath do item que se deseja esperar aperecer.
    :param opcao: Uma string com a opção que será marcada no item no item.
    """
    espera_aparecer(xpath)
    # Espera o item ficar 'clicável'
    wait.until(EC.element_to_be_clickable(('xpath', xpath)))
    try:
        Select(nav.find_element('xpath', xpath)).select_by_value(opcao)
    except Exception as e:
        print(xpath)
        print(e)



# Acessa o site da SomaSeg
nav.get('https://www.somaseg.com.br/user/login')
# Clica em 'Login'
clica('/html/body/header/div[2]/button')
# Preenche o campo 'Email'
escreve('//*[@id="email"]', email)
# Preenche o campo 'Senha'
escreve('//*[@id="senha"]', senha)
# Clica em 'Entrar'
clica('/html/body/div[1]/div/div[2]/form/div[3]/button')
# Clica no ícone de 'Relatórios'
clica('/html/body/nav/section/ul/li[20]/a')
# Clica em 'Alarmes e mensagens'
clica('//*[@id="tree"]/li/ul/li[1]/a')
# Marca a opção Tipo como 'Alarme'
seleciona('//*[@id="tipo"]', 'A')
# Preenche a data inicial e final da consulta
escreve('//*[@id="dataCentralIni"]', data)
escreve('//*[@id="dataCentralFim"]', data)
# Rola até o fim da página usando javascript
nav.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# Clica em 'Pesquisar'
clica('//*[@id="form-search"]/div[8]/div[4]/div/button[1]')
# Aguarda o carregamento da página
sleep(5)
# Clica em 'Marcar Providências'
clica('//*[@id="contentlayout"]/section[1]/div[5]/input[1]')
# Clica em 'Mostar ação de início de tratamento'
clica('//*[@id="mostrarAcaoInicio"]')
# Clica em 'Gerar planilha'
clica('//*[@id="contentlayout"]/section[1]/div[5]/a[2]')
# Renomeia o arquivo
for _ in range(20):
    try:
        rename(nome_ant, nome_novo)
        break
    except FileNotFoundError:
        # Aguarda o download do arquivo
        sleep(10)
    except Exception as e:
        print(e)
        break

