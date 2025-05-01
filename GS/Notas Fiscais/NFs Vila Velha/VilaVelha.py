from os import listdir, path, mkdir, rename, getcwd, remove
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from datetime import datetime
from PyPDF2 import PdfReader
from time import sleep

# Inicializa o navegador
service = Service(ChromeDriverManager().install())
options = Options()
options.add_experimental_option("prefs", {
    "download.default_directory": f'{getcwd()}\\notas',
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True  # Abre o PDF no visualizador padrão
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


def interact(action: str, xpath: str, keys: str = None) -> None:
    """
    Interage com determinado elemento na tela.
    Primeiro chama a função 'espera_aparecer' para não causar erro de Not Found.
    :param xpath: Uma string com o xpath do elemento que se deseja esperar aperecer.
    """
    actions = ['click', 'write', 'clear']
    if action not in actions:
        raise TypeError(f'{action} must be in {actions}')
    espera_aparecer(xpath)
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
    # Converte a data no modelo dd/mm/YYYY para uma variável do tipo datetime
    data = datetime(int(dados['Data'][6:]), int(dados['Data'][3:5]), int(dados['Data'][:2]))

def run():
    # Verifica se a pasta de destino das notas já existe
    if not path.exists('notas'):
        mkdir('notas')
    # Vai para o site
    nav.get('https://tributacao.vilavelha.es.gov.br/tbw/loginCNPJContribuinte.jsp?execobj=ContribuintesWebRelacionados')
    # Cria uma variável que aponta para a janela principal
    main_window = nav.current_window_handle
    # Aguarda o carregamento do site.
    espera_aparecer('//*[@id="usuario"]')
    while nav.find_elements('xpath', '/html/body/div/div/div[1]/form/div/div[9]/a[1]'):
        # Preenche as credenciais
        interact('clear', '//*[@id="usuario"]')
        interact('write', '//*[@id="usuario"]', dados['LOGIN'])
        interact('clear', '//*[@id="senha"]')
        interact('write', '//*[@id="senha"]', dados['SENHA'])
        interact('write', '/html/body/div/div/div[1]/form/div/div[7]/input', '')
        sleep(10)
        # Clica em Confirmar.
        interact('click', '/html/body/div/div/div[1]/form/div/div[9]/a[1]')

    # Clica em 'Nota Fiscal'
    interact('click', '//*[@id="divnotafiscalinner"]')
    # Clica em 'Listar Notas Fiscais'
    interact('click', '//*[@id="divlistanfinner"]')
    # Espera a tabela aparecer
    espera_aparecer('//*[@id="_tabcontent1"]')
    '''
    A tabela está no formato:
    NF
                NF              Situação    Data Emissão  Data Vencimento  Tomador                              CNPJ/CPF              CFPS  ISS Retido               RPS  Total da Nota          ISS         IRRF          PIS       COFINS         CSLL         INSS serie   Cód.Interno Chave Validação    
     xxxx  Normal/Cancelado     Nome do Condomínio      CNPJ         valores...
      .          .                     .                  .               .
      .          .                     .                  .               .
      .          .                     .                  .               .
     xxxx  Normal/Cancelado     Nome do Condomínio      CNPJ         valores...
     
    Então é realizado um .split('\n') no texto para quebrar as linhas e são guardadas apenas as linhas 2 até a 13, pois são
    as que contém dados das notas.
    As informações da tabela podem ser obtidas da seguinte forma:
    -> Número da NF: linha.split()[0]
    -> Situação: linha.split()[1]
    -> Data de Emissão: linha.split()[2]
    -> Nome do condomínio:
            for idx in range(22, len(row)):
                if row[idx].isnumeric():
                    break
            nome_condominio = row[23:idx-1])
    '''
    # O total de páginas está no final da tabela, então pode ser acessado com elemento.split('\n')[-4]
    tot_pags = int(nav.find_element('xpath', '//*[@id="_tabcontent1"]').text.split('\n')[-4])
    for pag in range(tot_pags):
        notas = nav.find_element('xpath', '//*[@id="_tabcontent1"]').text.split('\n')[2:14]
        for i, nota in enumerate(notas, start=1):
            # Acessa a emissão e converte para datetime
            emissao = nota.split()[2]
            emissao = datetime(int(emissao[6:]), int(emissao[3:5]), int(emissao[:2]))
            # Se já passou da data desejada, fecha o navegador e encerra a execução.
            if emissao < data:
                sleep(1)
                nav.quit()
                return

            situacao = nota.split()[1]
            if situacao == 'Normal' and data == emissao:
                # Marca a nota clicando no quadrado à sua esquerda.
                interact('click', f'//*[@id="{i},-1_gridListaFoco"]')
                # Clica em 'Visualizar/Imprimir notas selecionadas' (o símbolo é uma impressora).
                interact('click', '//*[@id="imagebutton7"]')
                # Aguarda o download.
                sleep(3)
                # Procura a nova janela.
                for window in nav.window_handles:
                    if window != main_window:
                        # Muda o contexto para a nova janela.
                        nav.switch_to.window(window)
                        # Feche a nova janela.
                        nav.close()
                        # Volta para a janela original.
                        nav.switch_to.window(main_window)
                        break
                # Desmarca a nota clicando no quadrado à sua esquerda.
                # Dá uma pausa antes e após clicar para evitar bugs que acontecem quando se clica muito rápido.
                sleep(0.5)
                interact('click', f'//*[@id="{i},-1_gridListaFoco"]')
                sleep(0.5)
        # Clica na seta para avançar para a próxima páina.
        interact('click', '//*[@id="gridLista"]/div[2]/div[1]/div/ul/li[7]/a')
        sleep(2)


run()

# ------------------------------------------------------------
# Lê cada pdf, encontra a razão social e o move para sua pasta
notas = [nota for nota in listdir('notas') if '.pdf' in nota]
for nota in notas:
    arq = f'notas/{nota}'

    with open(arq, 'rb') as file:
        # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
        pdf_reader = PdfReader(file)
        # Extrai o texto do PDF
        rows = pdf_reader.pages[0].extract_text().split('\n')

    # Acessa o nome da empresa, do condominio e o número da nota fiscal.
    # Procura o nome da empresa
    for i, row in enumerate(rows):
        if 'CNPJ/CPF:' in row:
            empresa = rows[i+1]
            break
    # Procura o nome do condomínio
    for row in rows[10:]:
        if 'CNPJ/CPF:' in row:
            condominio = row[9:]
            break
    # Procura o número da nofa fiscal
    for row in rows:
        if 'Data Emissão' in row:
            num_nf = row[:4]
            break
    # Verifica se ja há uma pasta para esta empresa
    if not path.exists(f'notas/{empresa}'):
        mkdir(f'notas/{empresa}')
    # Verifica se o arquivo já existe na pasta.
    if not path.exists(f'notas/{empresa}/{condominio}-{num_nf}.pdf'):
        # Move o arquivo para a nova pasta
        rename(arq, f'notas/{empresa}/{condominio}-{num_nf}.pdf')
