from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from os import listdir, rename
from time import sleep

with open('config.txt', 'r') as file:
    credenciais = file.read().split('\n')

# Separa as chaves dos valores
credenciais = [item.split('->') for item in credenciais]
# Atribui cada chave ao seu valor
credenciais = {chave: valor.strip() for chave, valor in credenciais}

# Verifica se a competencia está correta
meses = ['jan', 'fev', 'mar', 'abr',
         'mai', 'jun', 'jul', 'ago',
         'set', 'out', 'nov', 'dez']
assert credenciais['Competencia'] in meses, f'A competência precisa esta na forma:\n{meses}'

# Simbolo de carregamento
# //*[@id="mpProgressoContentTable"]/tbody/tr/td/div

path = credenciais['Diretorio']

# Configurações do Chrome
options = Options()
options.add_argument('--disable-extensions')
options.add_argument('--disable-popup-blocking')
options.add_argument('--disable-infobars')
options.add_argument('--safebrowsing-disable-download-protection')
options.add_argument('--safebrowsing-disable-extension-blacklist')
options.add_argument('--safebrowsing-manual-download-blacklist')
options.add_argument('--start-maximized')
options.add_experimental_option('prefs', {
    'download.default_directory': path,
    'download.prompt_for_download': False,
    'download.directory_upgrade': True,
    'safebrowsing.enabled': True
})
service = Service(ChromeDriverManager().install())

nav = webdriver.Chrome(service=service, options=options)

wait = WebDriverWait(nav, 30)


def clica(xpath: str, n: int = 50) -> None:
    """
    Tenta até n vezes clicar no botão com xpath passado no campo 'xpath'
    tendo uma pausa de 0.5s entre cada tentativa
    """
    wait.until(EC.element_to_be_clickable(('xpath', xpath)))
    sleep(0.5)
    for _ in range(n):
        try:
            nav.find_element('xpath', xpath).click()
            return
        except Exception as e:
            sleep(0.5)
    print(f'Erro ao clicar em {xpath}')


def escolhe_mes(mes: str) -> None:
    """
    Clica no mês correto para a consulta
    """
    # Clica na competência
    clica('//*[@id="consultarnfseForm:competenciaHeader"]/label/div')
    # Escolhe o mês correto:
    if mes == 'jan':
        clica('//*[@id="consultarnfseForm:competenciaDateEditorLayoutM0"]')
    elif mes == 'fev':
        clica('//*[@id="consultarnfseForm:competenciaDateEditorLayoutM1"]')
    elif mes == 'mar':
        clica('//*[@id="consultarnfseForm:competenciaDateEditorLayoutM2"]')
    elif mes == 'abr':
        clica('//*[@id="consultarnfseForm:competenciaDateEditorLayoutM3"]')
    elif mes == 'mai':
        clica('//*[@id="consultarnfseForm:competenciaDateEditorLayoutM4"]')
    elif mes == 'jun':
        clica('//*[@id="consultarnfseForm:competenciaDateEditorLayoutM5"]')
    elif mes == 'jul':
        clica('//*[@id="consultarnfseForm:competenciaDateEditorLayoutM6"]')
    elif mes == 'ago':
        clica('//*[@id="consultarnfseForm:competenciaDateEditorLayoutM7"]')
    elif mes == 'set':
        clica('//*[@id="consultarnfseForm:competenciaDateEditorLayoutM8"]')
    elif mes == 'out':
        clica('//*[@id="consultarnfseForm:competenciaDateEditorLayoutM9"]')
    elif mes == 'nov':
        clica('//*[@id="consultarnfseForm:competenciaDateEditorLayoutM10"]')
    elif mes == 'dez':
        clica('//*[@id="consultarnfseForm:competenciaDateEditorLayoutM11"]')


def run():
    # Vai para o site do ISS Fortaleza
    nav.get('https://iss.fortaleza.ce.gov.br/grpfor/login.seam?cid=928590')
    # Aguarda o site carregar
    sleep(1)
    # Verifica se está na página de Login
    while nav.find_elements('xpath', '//*[@id="login:botaoEntrar"]'):
        # Preenche as informações de Login
        nav.find_element('xpath', '//*[@id="login:password"]').clear()  # Limpa a senha atual
        nav.find_element('xpath', '//*[@id="login:username"]').send_keys(credenciais['LOGIN ISS'])
        nav.find_element('xpath', '//*[@id="login:password"]').send_keys(credenciais['SENHA ISS'])
        nav.find_element('xpath', '//*[@id="login:captchaDecor:captchaLogin"]').send_keys()
        # Espera o usuário preencher o captcha
        sleep(10)
    # Aguarda o carregamento da página
    sleep(1)

    # Extrai os cnpjs a partir de uma tabela
    cnpjs = nav.find_element('xpath', '//*[@id="alteraInscricaoForm"]').text.split('\n')
    cnpjs = cnpjs[5::3]

    achou = False
    for i, cnpj in enumerate(cnpjs):
        cnpj_num = ''.join([c for c in cnpj if c.isnumeric()])

        if cnpj == credenciais['CNPJ'] or cnpj_num == credenciais['CNPJ']:
            achou = True
            clica(f'//*[@id="alteraInscricaoForm:empresaDataTable:{i}:linkDocumento"]')
            # Aguarda o carregamento da página
            sleep(0.5)
            break

    if not achou:
        return

    # Clica em 'Consultar NFS-e'
    clica('//*[@id="homeForm:divHotLinks"]/div[4]')
    # Clica em 'Competência/Tomador'
    clica('//*[@id="consultarnfseForm:competencia_prestador_tab_lbl"]')
    # Aguarda o carregamento da página
    sleep(1)
    escolhe_mes(credenciais['Competencia'])
    # clica em 'OK'
    clica('//*[@id="consultarnfseForm:competenciaDateEditorButtonOk"]/span')
    # Clica em 'Consultar'
    clica('//*[@id="consultarnfseForm:j_id231"]')
    # Aguarda o fim da consulta
    wait.until(EC.invisibility_of_element_located(('xpath', '//*[@id="mpProgressoContentTable"]/tbody/tr/td/div')))

    ## Verifica quantas páginas existem

    # Verifica se tem menos que 10 páginas
    '''
    A tabela está na forma '<< < 1 2 3 4 5 6 7 8 9 10 > >>', o atributo .text contém essa string do item da tela,
    a função split() separa os itens, criando uma lista, e a slicing [2:-2] guarda apenas a lista
    ['1', '2', '3', ..., '9', '10']. 
    Se a consulta houver mais que 10 páginas, precisa ser verificada avançando as páginas, mas se tiver menos
    que 10, a lista conterá apenas os valores até a última página. Ex: só tem 4 páginas -> ['1', '2', '3', '4'].
    '''
    items = nav.find_element('xpath', '//*[@id="consultarnfseForm:dataTable:j_id368_table"]').text.split()[2:-2]

    if '10' in items:
        # Clica em '>>' para ir para a última página
        clica('//*[@id="consultarnfseForm:dataTable:j_id368_table"]/tbody/tr/td[16]')
        n_pags = int(nav.find_element('xpath',
                                      '//*[@id="consultarnfseForm:dataTable:j_id368_table"]').text.split()[-3])
        next_page = '//*[@id="consultarnfseForm:dataTable:j_id368_table"]/tbody/tr/td[15]'
        # Volta para a primeira página
        clica('//*[@id="consultarnfseForm:dataTable:j_id368_table"]/tbody/tr/td[1]')
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
            clica(next_page)
        wait.until(EC.invisibility_of_element_located(('xpath', '//*[@id="mpProgressoContentTable"]/tbody/tr/td/div')))
        sleep(1)
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
        n_items = 10
        # Verifica se há menos que 10
        for i, item in enumerate(items, start=1):
            if '«« « ' in item:
                n_items = 10 - i
                items = items[:n_items]
                break

        if pag > 0:
            sleep(1)
            # Clica em '««' para voltar para a primeira página
            clica('//*[@id="consultarnfseForm:dataTable:j_id368_table"]/tbody/tr/td[1]')

        for i, item in enumerate(items):
            #
            print(pag, item.split()[2], item.split()[1], ' '.join(item.split()[4:-2]))
            #
            # Verifica se a nota foi cancelada
            if item.split()[2] == 'CANCELADA':
                continue
            # Verifica se a nota já foi baixada
            nome_emp = ' '.join(item.split()[4:-2])
            num_nf = item.split()[1]
            if f'{nome_emp}-{num_nf}.pdf' in listdir(path):
                continue
            # Clica em '>' para avançar até a página correta
            for _ in range(pag):
                clica(next_page)
            # Clica no símbolo de lupa da Nota Fiscal
            clica(f'//*[@id="consultarnfseForm:dataTable:{i}:j_id360"]')
            # Clica em 'Exportar para PDF'
            clica('//*[@id="j_id157:panelAcoes"]/tbody/tr/td[1]/input')
            # Renomeia o Arquivo
            nome_ant = fr'{path}\relatorio.pdf'
            nome_arq = fr'{path}\{nome_emp}-{num_nf}.pdf'
            for _ in range(20):
                # Tenta renomear a nota, caso ela ainda esteja sendo baixada, espera
                # 0.5 segundos e tenta novamente.
                try:
                    rename(nome_ant, nome_arq)
                    break
                except Exception as e:
                    sleep(0.5)
            # Clica em 'Voltar'
            clica('//*[@id="j_id157:panelAcoes"]/tbody/tr/td[2]/input')
            # Clica em 'Competência/Tomador'
            clica('//*[@id="consultarnfseForm:competencia_prestador_tab_lbl"]')
            # Aguarda o carregamento
            wait.until(
                EC.invisibility_of_element_located(('xpath', '//*[@id="mpProgressoContentTable"]/tbody/tr/td/div')))
            escolhe_mes(credenciais['Competencia'])
            # clica em 'OK'
            clica('//*[@id="consultarnfseForm:competenciaDateEditorButtonOk"]/span')
            # Clica em 'Consultar'
            clica('//*[@id="consultarnfseForm:j_id231"]')
            # Aguarda o fim da consulta
            wait.until(
                EC.invisibility_of_element_located(('xpath', '//*[@id="mpProgressoContentTable"]/tbody/tr/td/div')))

        if pag > 0:
            sleep(0.5)
            # Clica em '««' para voltar para a primeira página
            clica('//*[@id="consultarnfseForm:dataTable:j_id368_table"]/tbody/tr/td[1]')

    sleep(5)


run()
