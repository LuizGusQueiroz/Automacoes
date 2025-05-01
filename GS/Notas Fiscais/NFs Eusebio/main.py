from os import listdir, path, mkdir, rename, getcwd, remove
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
from PyPDF2 import PdfReader
from time import sleep

def main():

    # Inicializa o navegador
    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": f'{getcwd()}\\notas',
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_setting_values.automatic_downloads": 1
    })
    nav = webdriver.Chrome(options=options)


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


    def interact(action: str, xpath: str, keys: str = None, n_tries: int = 10) -> None:
        """
        Interage com determinado elemento na tela.
        Primeiro chama a função 'espera_aparecer' para não causar erro de Not Found.
        :param xpath: Uma string com o xpath do elemento que se deseja esperar aperecer.
        """
        actions = ['click', 'write', 'clear']
        if action not in actions:
            raise TypeError(f'{action} must be in {actions}')
        espera_aparecer(xpath)
        for try_i in range(n_tries):
            try:
                # Find the element
                element = nav.find_element('xpath', xpath)
                # Choose the right action to do
                if   action == 'click':
                    element.click()
                elif action == 'write':
                    element.send_keys(keys)
                elif action == 'clear':
                    element.clear()
                return
            except NoSuchElementException:
                if try_i == n_tries - 1:
                    print(f'Item com xpath {xpath} não encontrado')
                sleep(1)
            except ElementNotInteractableException:
                if try_i == n_tries - 1:
                    print(f'Elemento com xpath {xpath} indisponível ou oculto.')
                sleep(1)
            except ElementClickInterceptedException:
                if try_i == n_tries - 1:
                    print(f'Elemento com xpath {xpath} interceptado ou sobreposto.')
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
        data = datetime(int(dados['Data'][6:]), int(dados['Data'][3:5]), int(dados['Data'][:2]))

    #------------------------------------
    # Verifica se as pata de destino das notas já existe
    if not path.exists('notas'):
        mkdir('notas')
    nav.get('https://iss.speedgov.com.br/eusebio/login')
    # Preenche o login
    interact('write', '//*[@id="inscricao"]', dados['LOGIN'])
    # Preenche a senha
    interact('write', '//*[@id="senha"]', dados['SENHA'])
    # Clica em 'Entrar'.
    interact('click', '/html/body/div[1]/div[1]/div[1]/div[2]/form/button')
    # Clica em 'Área do Prestador'.
    interact('click', '/html/body/div[2]/aside[1]/div/nav/ul/li[2]/a')
    # Clica em 'Notas Fiscais'.
    interact('click', '//*[@id="item1"]/li[2]/a')
    # Escolhe a competência desejada.
    Select(nav.find_element('xpath', '//*[@id="q_nfecompmes_eq"]')).select_by_visible_text(dados['Competencia'])
    # Clica em 'Filtrar'.
    interact('click', '//*[@id="nota_fiscal_search"]/div[2]/input')
    # Verifica quantas páginas existem
    if nav.find_elements('xpath', '/html/body/div[2]/section/div/div[3]/div/div/nav/ul'):
        n_pags = int(nav.find_element('xpath', '/html/body/div[2]/section/div/div[3]/div/div/nav/ul').text.split('\n')[-2])
    else:
        n_pags = 1
    # Indicador do fim das notas
    acabou = False
    # Percorre todas as páginas
    for pag in range(n_pags):
        if n_pags > 1:
            # Guarda o botão de próxima página.
            next_page = nav.find_element(By.CSS_SELECTOR,
            'body > div.wrapper > section > div > div.card.card-default > div > div > nav > ul > li.next.next_page.page-item')
        # Conta quantas notas há na tabela
        table = nav.find_element('xpath', '/html/body/div[2]/section/div/div[3]/div/div').text.split('\n')[1:]
        for i, row in enumerate(table):
            if row == '<':
                table = table[:i]
                break
        n_notas = int(len(table) / 3)
        # Percorre todas as notas
        for idx in range(1, n_notas+1):
            # Verifica se a data é a mesma
            data_i = table[3*idx-3].split()[1]
            data_i = datetime(int(data_i[6:]), int(data_i[3:5]), int(data_i[:2]))
            if data_i == data:
                interact('click',
                   f'/html/body/div[2]/section/div/div[3]/div/div/table/tbody/tr[{idx}]/td[12]/div/a[1]/button')
            elif data_i < data:
                acabou = True
                break
            sleep(1)
        sleep(3)
        # Renomeia as notas
        for nota in [file for file in listdir('notas') if '.pdf' in file]:
            nota = f'notas/{nota}'
            with open(nota, 'rb') as file:
                # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
                pdf_reader = PdfReader(file)
                # Extrai o texto do PDF
                rows = pdf_reader.pages[0].extract_text().split('\n')
            # Encontra o número da nota
            for i, row in enumerate(rows):
                if 'DADOS DO TOMADOR' in row:
                    num_nf = rows[i + 1][-4:]
                    break
            # Encontra o nome do condomínio
            for row in rows:
                if 'Competência' in row:
                    condominio = row[:row.find('Competência')]
                    break
            # Encontra o nome da empresa
            for row in rows:
                if 'Nome Fantasia' in row:
                    empresa = row[row.find('Nome Fantasia') + 13:]
                    break
            # Verifica se ja há uma pasta para esta empresa
            if not path.exists(f'notas/{empresa}'):
                mkdir(f'notas/{empresa}')
            # Verifica se o arquivo já existe na pasta.
            if not path.exists(f'notas/{empresa}/{condominio} - {num_nf} adm.pdf'):
                # Move o arquivo para a nova pasta
                try:
                    rename(nota, f'notas/{empresa}/{condominio} - {num_nf} adm nf.pdf')
                except FileExistsError:
                    remove(nota)
            else: # Apaga a nota
                remove(nota)

        if acabou:
            break
        # Avança para a próxima página se não estiver na última.
        if pag != n_pags - 1:
            next_page.click()
    nav.quit()


main()
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
