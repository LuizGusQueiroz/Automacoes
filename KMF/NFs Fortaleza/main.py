from os import listdir, path, mkdir, rename, getcwd, remove
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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
    espera_aparecer(xpath)
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
            if try_i == n_tries - 1:
                raise Exception(f'Item com xpath {xpath} não encontrado')
            sleep(1)
        except ElementNotInteractableException:
            if try_i == n_tries - 1:
                raise Exception(f'Elemento com xpath {xpath} indisponível ou oculto.')
            sleep(1)
        except ElementClickInterceptedException:
            if try_i == n_tries - 1:
                raise Exception(f'Elemento com xpath {xpath} interceptado ou sobreposto.')
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


def escolhe_mes(mes: str) -> None:
    """
    Clica no mês correto para a consulta
    """
    # Clica na competência
    interact('click', '//*[@id="consultarnfseForm:competenciaHeader"]/label/div')
    wait.until(EC.element_to_be_clickable(('xpath',
                                           '//*[@id="consultarnfseForm:competenciaDateEditorLayoutM0"]')))
    # Escolhe o mês correto:
    if mes == 'jan':
        interact('click', '//*[@id="consultarnfseForm:competenciaDateEditorLayoutM0"]')
    elif mes == 'fev':
        interact('click', '//*[@id="consultarnfseForm:competenciaDateEditorLayoutM1"]')
    elif mes == 'mar':
        interact('click', '//*[@id="consultarnfseForm:competenciaDateEditorLayoutM2"]')
    elif mes == 'abr':
        interact('click', '//*[@id="consultarnfseForm:competenciaDateEditorLayoutM3"]')
    elif mes == 'mai':
        interact('click', '//*[@id="consultarnfseForm:competenciaDateEditorLayoutM4"]')
    elif mes == 'jun':
        interact('click', '//*[@id="consultarnfseForm:competenciaDateEditorLayoutM5"]')
    elif mes == 'jul':
        interact('click', '//*[@id="consultarnfseForm:competenciaDateEditorLayoutM6"]')
    elif mes == 'ago':
        interact('click', '//*[@id="consultarnfseForm:competenciaDateEditorLayoutM7"]')
    elif mes == 'set':
        interact('click', '//*[@id="consultarnfseForm:competenciaDateEditorLayoutM8"]')
    elif mes == 'out':
        interact('click', '//*[@id="consultarnfseForm:competenciaDateEditorLayoutM9"]')
    elif mes == 'nov':
        interact('click', '//*[@id="consultarnfseForm:competenciaDateEditorLayoutM10"]')
    elif mes == 'dez':
        interact('click', '//*[@id="consultarnfseForm:competenciaDateEditorLayoutM11"]')


def run():
    if not path.exists(dir):
        mkdir(dir)
    # Vai para o site do ISS Fortaleza
    nav.get(
        'https://idp2.sefin.fortaleza.ce.gov.br/realms/sefin/protocol/openid-connect/auth?nonce=5d91026e-7a08-412f-a50d-91cc2c2576c9&response_type=code&client_id=iss.sefin.fortaleza.ce.gov.br&redirect_uri=https%3A%2F%2Fiss.fortaleza.ce.gov.br%2Fgrpfor%2Foauth2%2Fcallback&scope=openid+profile&state=secret-eb17c44e-25ca-4b8c-bda8-46d8f4d5fee0')
    # Aguarda o site carregar
    sleep(1)
    # Verifica se está na página de Login
    while nav.find_elements('xpath', '//*[@id="botao-entrar"]'):
        # Preenche as informações de Login
        interact('clear', '//*[@id="username"]')  # Limpa a senha atual
        interact('write', '//*[@id="username"]', dados['LOGIN'])
        interact('write', '//*[@id="password"]', dados['SENHA'])
        # Clica em entrar
        interact('click', '//*[@id="botao-entrar"]')
        sleep(1)
    # Aguarda o carregamento da página
    sleep(2)
    # Clica em 'Fazer Login'
    interact('click', '//*[@id="login"]/div[1]/div[2]/a[1]')
    sleep(2)
    # Conta quantas páginas de CNPJ existem
    if nav.find_elements('xpath', '//*[@id="alteraInscricaoForm:empresaDataTable:j_id383_table"]'):
        try:
            n_pags = int(nav.find_element(
                'xpath', '//*[@id="alteraInscricaoForm:empresaDataTable:j_id383_table"]').text.split()[-2])
        except:
            n_pags = 10
    else:
        n_pags = 1
    for pag in range(n_pags):
        sleep(2)
        # Extrai os cnpjs a partir de uma tabela
        cnpjs = nav.find_element('xpath', '//*[@id="alteraInscricaoForm"]').text.split('\n')
        cnpjs = cnpjs[5::3]

        achou = False
        for i, cnpj in enumerate(cnpjs):
            cnpj_num = ''.join([c for c in cnpj if c.isnumeric()])

            if cnpj == dados['CNPJ'] or cnpj_num == dados['CNPJ']:
                achou = True
                interact('click', f'//*[@id="alteraInscricaoForm:empresaDataTable:{10 * pag + i}:linkDocumento"]')
                # Aguarda o carregamento da página
                sleep(0.5)
                break
        if achou:
            break
        # Avança para a próxima página
        if pag != n_pags - 1:
            interact('click', f'//*[@id="alteraInscricaoForm:empresaDataTable:j_id383_table"]/tbody/tr/td[{5 + pag}]')

    if not achou:
        print(f'CNPJ {dados['CNPJ']} não encontrado!')
        input()
        return

    # Clica em 'Consultar NFS-e'
    interact('click', '//*[@id="homeForm:divHotLinks"]/div[4]')
    # Clica em 'Competência/Tomador'
    interact('click', '//*[@id="consultarnfseForm:competencia_prestador_tab_lbl"]')
    # Aguarda o carregamento da página
    sleep(1)
    escolhe_mes(dados['Competencia'])
    # clica em 'OK'
    interact('click', '//*[@id="consultarnfseForm:competenciaDateEditorButtonOk"]/span')
    # Clica em 'Consultar'
    interact('click', '//*[@id="consultarnfseForm:j_id231"]')
    # Aguarda o fim da consulta
    wait.until(EC.invisibility_of_element_located(('xpath', '//*[@id="mpProgressoContentTable"]/tbody/tr/td/div')))
    ## Verifica quantas páginas existem
    '''
    A tabela está na forma '<< < 1 2 3 4 5 6 7 8 9 10 > >>', o atributo .text contém essa string do item da tela,
    a função split() separa os itens, criando uma lista, e a slicing [2:-2] guarda apenas a lista
    ['1', '2', '3', ..., '9', '10']. 
    Se a consulta houver mais que 10 páginas, precisa ser verificada avançando as páginas, mas se tiver menos
    que 10, a lista conterá apenas os valores até a última página. Ex: só tem 4 páginas -> ['1', '2', '3', '4'].
    '''
    items = nav.find_element('xpath', '//*[@id="consultarnfseForm:dataTable:j_id368_table"]').text.split()[2:-2]

    # Verifica se tem menos que 10 páginas
    if '10' in items:
        # Clica em '>>' para ir para a última página
        interact('click', '//*[@id="consultarnfseForm:dataTable:j_id368_table"]/tbody/tr/td[16]')
        # Aguarda o fim da consulta
        wait.until(
            EC.invisibility_of_element_located(('xpath', '//*[@id="mpProgressoContentTable"]/tbody/tr/td/div')))
        # Acessa o último número de página do rodapé da tabela
        n_pags = int(nav.find_element('xpath',
                                      '//*[@id="consultarnfseForm:dataTable:j_id368_table"]').text.split()[-3])
        next_page = '//*[@id="consultarnfseForm:dataTable:j_id368_table"]/tbody/tr/td[15]'
        # Volta para a primeira página
        interact('click', '//*[@id="consultarnfseForm:dataTable:j_id368_table"]/tbody/tr/td[1]')
    else:
        n_pags = int(items[-1])
        next_page = f'//*[@id="consultarnfseForm:dataTable:j_id368_table"]/tbody/tr/td[{15 - 10 + n_pags}]'

    # Percorre cada página
    for pag in range(n_pags):
        sleep(1)
        # Clica em '>' para avançar até a página correta
        for _ in range(pag):
            # Aguarda o fim da consulta
            wait.until(
                EC.invisibility_of_element_located(('xpath', '//*[@id="mpProgressoContentTable"]/tbody/tr/td/div')))
            interact('click', next_page)
        sleep(6)
        '''
        Em cada página há um tabela está na forma :
            Resultado da Consulta
            Data de Emissão
            Número da NFS-e
            Situação
            CPF/CNPJ do Tomador
            Nome Tomador
            Base de Cálculo
            Imposto
            «« « 1 2 3 4 5 6 7 8 9 » »»
            DD/MM/AAAA NumNF Situação CNPJ Nome da Empresa Base-Cálculo Impostos
            DD/MM/AAAA NumNF Situação CNPJ Nome da Empresa Base-Cálculo Impostos
            .
            .
            .
            DD/MM/AAAA NumNF Situação CNPJ Nome da Empresa Base-Cálculo Impostos            
            DD/MM/AAAA NumNF Situação CNPJ Nome da Empresa Base-Cálculo Impostos

        a função split('\n) separa os itens, criando uma lista, e a slicing [-10:] guarda apenas os últimos 10 
        elementos, que são os dados das Notas Fiscais.
        Em cada item desta lista, as seguintes informações podem ser extraídas:
            -> Data:            item.split()[0]
            -> Número da NF:    item.split()[1]
            -> Situação:        item.split()[2]
            -> CNPJ:            item.split()[4]
            -> Nome Empresa:    item.split()[5:-2]
            -> Base de Cálculo: item.split()[-2]
            -> Impostos:        item.split()[-1]
        '''
        items = nav.find_element('xpath', '//*[@id="id_dados_consulta"]').text.split('\n')[-10:]

        # Por padrão, há 10 items por página
        # Verifica se há menos que 10
        for i, item in enumerate(items, start=1):
            if '«« « ' in item:
                n_items = 10 - i
                items = items[:n_items]
                break

        if pag > 0:
            sleep(1)
            # Clica em '««' para voltar para a primeira página
            interact('click', '//*[@id="consultarnfseForm:dataTable:j_id368_table"]/tbody/tr/td[1]')

        for i, item in enumerate(items):
            print(pag, item.split()[0], item.split()[2], item.split()[1], ' '.join(item.split()[4:-2]))
            _ = item.split()[0]
            dia_i = datetime(int(_[6:]), int(_[3:5]), int(_[:2]))
            # Verifica se acabaram as notas
            if dia_i > dia:
                renomeia_notas()
                return
            # Verifica se a nota é do dia especificado
            if item.split()[0] != dados['Data']:
                continue
            # Verifica se a nota foi cancelada
            if item.split()[2] == 'CANCELADA':
                continue
            # Verifica se a nota já foi baixada
            nome_emp = ' '.join(item.split()[4:-2])
            num_nf = item.split()[1]
            if f'{nome_emp}-{num_nf}.pdf' in listdir(dir):
                continue

            # Clica em '>' para avançar até a página correta
            for _ in range(pag):
                # Aguarda o fim da consulta
                wait.until(
                    EC.invisibility_of_element_located(('xpath', '//*[@id="mpProgressoContentTable"]/tbody/tr/td/div')))
                interact('click', next_page)

            # Aguarda o fim da consulta
            wait.until(
                EC.invisibility_of_element_located(('xpath', '//*[@id="mpProgressoContentTable"]/tbody/tr/td/div')))
            # Clica no símbolo de lupa da Nota Fiscal
            interact('click', f'//*[@id="consultarnfseForm:dataTable:{i}:j_id360"]')
            # Clica em 'Exportar para PDF'
            interact('click', '//*[@id="j_id157:panelAcoes"]/tbody/tr/td[1]/input')
            sleep(1)
            # Clica em 'Voltar'
            interact('click', '//*[@id="j_id157:panelAcoes"]/tbody/tr/td[2]/input')
            # Clica em 'Competência/Tomador'
            interact('click', '//*[@id="consultarnfseForm:competencia_prestador_tab_lbl"]')
            # Aguarda o carregamento
            wait.until(
                EC.invisibility_of_element_located(('xpath', '//*[@id="mpProgressoContentTable"]/tbody/tr/td/div')))
            escolhe_mes(dados['Competencia'])
            # clica em 'OK'
            interact('click', '//*[@id="consultarnfseForm:competenciaDateEditorButtonOk"]/span')
            # Clica em 'Consultar'
            interact('click', '//*[@id="consultarnfseForm:j_id231"]')
            # Aguarda o fim da consulta
            wait.until(
                EC.invisibility_of_element_located(('xpath', '//*[@id="mpProgressoContentTable"]/tbody/tr/td/div')))

        if pag > 0:
            # Aguarda o fim da consulta
            wait.until(
                EC.invisibility_of_element_located(('xpath', '//*[@id="mpProgressoContentTable"]/tbody/tr/td/div')))
            # Clica em '««' para voltar para a primeira página
            interact('click', '//*[@id="consultarnfseForm:dataTable:j_id368_table"]/tbody/tr/td[1]')


def renomeia_notas():
    notas = [nota for nota in listdir('notas') if '.pdf' in nota]
    for nota in notas:
        arq = f'notas/{nota}'

        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            # Extrai o texto do PDF
            rows = pdf_reader.pages[0].extract_text().split('\n')

        num_nf = rows[4]
        for row in rows:
            if 'Regime especial Tributação' in row:
                nome = row[26:]
                break
        for row in rows:
            if 'E-mail' in row:
                empresa = row[row.rfind('E-mail') + 6:]
                break
        # Verifica se ja há uma pasta para esta empresa
        if not path.exists(f'notas/{empresa}'):
            mkdir(f'notas/{empresa}')
        # Verifica se o arquivo já existe na pasta.
        if not path.exists(f'notas/{empresa}/{nome}-{num_nf}.pdf'):
            # Move o arquivo para a nova pasta
            rename(arq, f'notas/{empresa}/{nome}-{num_nf}.pdf')
        else:
            remove(arq)


run()
