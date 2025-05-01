from os import listdir, path, mkdir, rename, getcwd, remove
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from PyPDF2 import PdfReader
from zipfile import ZipFile
from time import sleep


def main():
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


    def clica(xpath: str, n:int = 20) -> None:
        """
        Clica em determinado elemento na tela.
        Primeiro chama a função 'espera_aparecer' para não causar erro de Not Found.
        :param xpath: Uma string com o xpath do elemento que se deseja esperar aperecer.
        """
        espera_aparecer(xpath, n=n)
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
        clica('/html/body/div/div[3]/div/p[3]/a', n=5)
    except NoSuchElementException:
        # O botão não existe, não é necessário fazer nada
        pass
    # Clica em 'Acessar o sistema'
    try:
        clica('/html/body/div/div[3]/div/p[8]/a', n=5)
    except NoSuchElementException:
        # O botão não existe, não é necessário fazer nada
        pass

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
    nav.find_element('xpath', '//*[@id="form"]/fieldset/div/div[2]/p/input[2]').clear()
    nav.find_element('xpath', '//*[@id="form"]/fieldset/div/div[2]/p/input[2]').send_keys(dados['DataInicial'])
    # 'Até'
    nav.find_element('xpath', '//*[@id="form"]/fieldset/div/div[2]/p/input[3]').clear()
    nav.find_element('xpath', '//*[@id="form"]/fieldset/div/div[2]/p/input[3]').send_keys(dados['DataFinal'])
    # Clica em 'Buscar'
    clica('//*[@id="form"]/fieldset/div/div[3]/p/span/span/input')

    # Clica em marcar a opereção 'Baixar'
    clica('//*[@id="dvLote"]/div[2]/div[1]/p/input[2]')
    # Clica em 'Executar'
    clica('//*[@id="dvLote"]/div[2]/div[2]/p/span[1]/span/input')

    # Caminho para o arquivo zip
    caminho_arquivo_zip = fr'{getcwd()}\NFE_{dados["Inscricao"]}.zip'

    # Diretório de extração dos arquivos
    diretorio_destino = fr'{getcwd()}\notas'  # getcwd() retorna o diretório atual
    # Verifica se existe a pasta de origem das notas
    if not path.exists(diretorio_destino):
        # Cria a pasta
        mkdir(diretorio_destino)

    for _ in range(200):
        try:
            # Abre o arquivo zip
            with ZipFile(caminho_arquivo_zip, 'r') as file:
                # Extrai os arquivos
                file.extractall(diretorio_destino)
            break
        except FileNotFoundError:
            # Aguarda o download do arquivo
            sleep(5)
        except Exception as e:
            print(e)
            break


    # Lê cada pdf, encontra a razão social e o move para sua pasta
    notas = [nota for nota in listdir('notas') if '.pdf' in nota]
    for nota in notas:
        arq = f'notas/{nota}'

        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            # Extrai o texto do PDF
            pags = pdf_reader.pages[0].extract_text().split('\n')

        # Acessa o nome da empresa, do condominio e o número da nota fiscal.
        empresa = pags[11][18:]
        condominio = pags[18][18:]
        num_nf = pags[4].split()[0]
        # Verifica se ja há uma pasta para esta empresa
        if not path.exists(f'notas/{empresa}'):
            mkdir(f'notas/{empresa}')
        # Verifica se o arquivo já existe na pasta.
        if not path.exists(f'notas/{empresa}/{condominio}-{num_nf}.pdf'):
            # Move o arquivo para a nova pasta
            rename(arq, f'notas/{empresa}/{condominio}-{num_nf}.pdf')
    # Apaga o arquivo zip
    remove(fr'{getcwd()}\NFE_{dados["Inscricao"]}.zip')
    # Apaga os arquivos remanescentes
    files = [fr'notas\{file}' for file in listdir('notas') if not path.isdir(f'notas\\{file}')]
    for file in files:
        remove(file)
    # Fecha o navegador
    nav.quit()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        input()