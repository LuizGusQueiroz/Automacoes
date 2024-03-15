from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from os import listdir, path, mkdir, rename, getcwd, remove
from time import sleep
from zipfile import ZipFile
from PyPDF2 import PdfReader

# Inicializa o navegador
service = Service(ChromeDriverManager().install())
nav = webdriver.Chrome(service=service)


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
    try:
        nav.find_element('xpath', xpath).click()
    except Exception as e:
        print(e)


# Lê as credenciais de acesso
with open('config.txt', 'r') as file:
    # Separa o arquivo por linha
    dados = file.read().split('\n')
    # Separa cada chave de seu valor
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
clica('/html/body/div/div[3]/div/p[3]/a')

espera_aparecer('//*[@id="DataTables_Table_0_wrapper"]')
'''
É exibida uma tabela com a listagem de empresas no login para se escolher qual empresa se deseja acessar.
Após o .split('\n), a tabela fica na forma:
    10
    25
    50
    100
    resultados por página
    Razão Social            Inscrição      Último acesso
    NOME PRIMEIRA EMPRESA   NUM-INSCRIÇÃO dd/mm/aaaa
    NOME SEGUNDA  EMPRESA   NUM-INSCRIÇÃO dd/mm/aaaa
    .               .               .          .
    .               .               .          .
    .               .               .          .
    NOME N-ÉSIMA  EMPRESA   NUM-INSCRIÇÃO dd/mm/aaaa
    Mostrando de 1 até 2 de 2 registros
    Anterior1Próximo
    
O slicing [6:-2] guarda apenas as linhas com os dados das empresas para se decidir em qual clicar
'''
empresas = nav.find_element('xpath', '//*[@id="DataTables_Table_0_wrapper"]').text.split('\n')[6:-2]

for i, empresa in enumerate(empresas, start=1):
    inscricao = empresa.split()[-2]
    if inscricao == dados['Inscricao']:
        # Clica na linha da empresa correta
        clica(f'//*[@id="DataTables_Table_0"]/tbody/tr[{i}]/td[1]')
        break

# Clica em 'Operar Lotes'
clica('/html/body/div[1]/div[4]/div/div/div[1]/div[1]/div[2]/div/div/div[1]/h3/a')

# Clica em 'Data de Emissão'
clica('//*[@id="form"]/fieldset/div/div[2]/p/input[1]')
# Preenche o intervalo
# 'De'
nav.find_element('xpath', '//*[@id="form"]/fieldset/div/div[2]/p/input[2]').send_keys(dados['DataInicial'])
# 'Até'
nav.find_element('xpath', '//*[@id="form"]/fieldset/div/div[2]/p/input[3]').send_keys(dados['DataFinal'])

# Clica em 'Buscar'
clica('//*[@id="form"]/fieldset/div/div[3]/p/span/span/input')

# Clica em marcar a opereção 'Baixar'
clica('//*[@id="dvLote"]/div[2]/div[1]/p/input[2]')
# Clica em 'Executar'
clica('//*[@id="dvLote"]/div[2]/div[2]/p/span[1]/span/input')

# Caminho para o arquivo zip
caminho_arquivo_zip = fr'{dados['Downloads']}\NFE_{dados["Inscricao"]}.zip'

# Diretório de extração dos arquivos
diretorio_destino = fr'{getcwd()}\notas'  # getcwd() retorna o diretório atual
for _ in range(200):
    try:
        # Abre o arquivo zip
        with ZipFile(caminho_arquivo_zip, 'r') as file:
            # Extrai os arquivos
            file.extractall(diretorio_destino)
        break
    except FileNotFoundError:
        # Aguarda o download do arquivo
        sleep(10)
    except Exception as e:
        print(e)
        break

# Verifica se existe a pasta de destino das notas
if not path.exists('empresas'):
    # Cria a pasta
    mkdir('empresas')
# Lê cada pdf, encontra a razão social e o move para sua pasta
notas = [nota for nota in listdir('notas') if '.pdf' in nota]
for nota in notas:
    arq = f'notas/{nota}'

    with open(arq, 'rb') as file:
        # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
        pdf_reader = PdfReader(file)
        # Extrai o texto do PDF
        pags = pdf_reader.pages[0].extract_text().split('\n')

    # Encontra a linha que contém o nome do condomínio
    for pag in range(len(pags)):
        if 'Nome/Razão Social ' in pags[pag]:
            razao = pags[pag].split('Nome/Razão Social ')[1]
            # Verifica se ja há uma pasta para esta empresa
            if not path.exists(f'empresas/{razao}'):
                mkdir(f'empresas/{razao}')
            # Verifica se o arquivo já está na pasta
            if not path.exists(f'empresas/{razao}/{nota}'):
                # Move o arquivo para a nova pasta
                rename(arq, f'empresas/{razao}/{nota}')
            # Encerra a procura da razão social
            break
# Apaga o arquivo zip
remove(fr'{dados['Downloads']}\NFE_{dados["Inscricao"]}.zip')
# Apaga os arquivos
files = [fr'notas\{file}' for file in listdir('notas')]
for file in files:
    remove(file)

