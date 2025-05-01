from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from typing import List, Dict, Callable
from selenium import webdriver
from datetime import datetime
from PyPDF2 import PdfReader
from time import sleep
from tqdm import tqdm
import pandas as pd
import os


def main() -> None:
    nav, wait = start_nav()
    dados: Dict = get_creds()
    def interact(action: str, xpath: str, keys: str = None, n_tries: int = 10):
        _interact(nav, wait, action, xpath, keys, n_tries)

    run(nav, wait, dados, interact)
    renomeia_notas(dados['Modelo_Nome'])
    atualiza_relatorio()


def run(nav, wait, dados: Dict, interact: Callable) -> None:
    # Vai para o site do ISS Fortaleza
    nav.get(
        'https://idp2.sefin.fortaleza.ce.gov.br/realms/sefin/protocol/openid-connect/auth?nonce=5d91026e-7a08-412f-a50d-91cc2c2576c9&response_type=code&client_id=iss.sefin.fortaleza.ce.gov.br&redirect_uri=https%3A%2F%2Fiss.fortaleza.ce.gov.br%2Fgrpfor%2Foauth2%2Fcallback&scope=openid+profile&state=secret-eb17c44e-25ca-4b8c-bda8-46d8f4d5fee0')
    # Aguarda o site carregar
    sleep(1)
    # Verifica se está na página de Login
    while nav.find_elements('xpath', '//*[@id="botao-entrar"]'):
        # Preenche as informações de Login
        interact('clear', '//*[@id="username"]')  # Limpa o login atual
        interact('write', '//*[@id="username"]', dados['LOGIN'])
        interact('clear', '//*[@id="password"]')  # Limpa a senha atual
        interact('write', '//*[@id="password"]', dados['SENHA'])
        # Clica em entrar
        interact('click', '//*[@id="botao-entrar"]', n_tries=10)
        sleep(1)
    # Aguarda o carregamento da página
    sleep(2)
    # Clica em 'Fazer Login'
    interact('click', '//*[@id="login"]/div[1]/div[2]/a[1]')
    sleep(2)
    # Verifica se a tabela de CNPJ existe.
    if nav.find_elements('xpath', '//*[@id="alteraInscricaoForm:empresaDataTable"]'):
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
            sleep(3)  # Extrai os cnpjs a partir de uma tabela
            cnpjs = nav.find_element('xpath', '//*[@id="alteraInscricaoForm"]').text.split('\n')
            cnpjs = cnpjs[5::3]

            achou = False
            for i, cnpj in enumerate(cnpjs):
                cnpj_num = ''.join([c for c in cnpj if c.isnumeric()])

                if cnpj == dados['CNPJ'] or cnpj_num == dados['CNPJ']:
                    achou = True
                    interact('click',
                             f'//*[@id="alteraInscricaoForm:empresaDataTable:{10 * pag + i}:linkDocumento"]')
                    # Aguarda o carregamento da página
                    sleep(0.5)
                    break
            if achou:
                break
            # Avança para a próxima página
            if pag != n_pags - 1:
                interact('click',
                         f'//*[@id="alteraInscricaoForm:empresaDataTable:j_id383_table"]/tbody/tr/td[{5 + pag}]')

        if not achou:
            print(f'CNPJ {dados['CNPJ']} não encontrado!')
            input()
            return

        # Clica em 'Escrituração'
        interact('click', '//*[@id="navbar"]/ul/li[6]/a')
        # Clica em 'Manter Escrituração'
        interact('click', '//*[@id="formMenuTopo:menuEscrituracao:j_id78"]')
        # Clica em 'Consultar'
        interact('click', '//*[@id="manterEscrituracaoForm:btnConsultar"]')
        # Clica em 'Visualizar'.
        interact('click', '//*[@id="manterEscrituracaoForm:dataTable:0:visualizar"]')
        # Clica em 'Serviços Prestados'.
        interact('click', '//*[@id="abaServicosPrestados_lbl"]')
        sleep(1)
        # Seleciona a situação 'Normal'.
        Select(nav.find_element('xpath', '//*[@id="servicos_prestados_form:comboStatusDocumento"]'
                                )).select_by_visible_text('Normal')
        # Seleciona em 'Outros Filtros: ' a opção 'Dia'.
        Select(nav.find_element('xpath', '//*[@id="servicos_prestados_form:comboOutroFiltroSelecionado"]'
                                )).select_by_visible_text('Dia')
        # Preenche a data.
        interact('write', '//*[@id="servicos_prestados_form:dataInicialInputDate"]', dados['Data'])
        # Clica em 'Pesquisar'.
        interact('click', '//*[@id="servicos_prestados_form:j_id514"]')
        # Aguarda o carregamento da pesquisa.
        wait.until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="mpProgressoContentTable"]/tbody/tr/td/div')))
        espera_aparecer(nav, wait, '//*[@id="servicos_prestados_form:datatable_servico_prestado:tb"]')
        # Conta quantas páginas tem pelo tamanho do rodapé.
        n_pags = len(nav.find_element('xpath', '//*[@id="servicos_prestados_form:datatable_servico_prestado:j_id614_table"]').text.split()) - 4
        # Quando há apenas uma página, o índice não aparece, então fica com 0 páginas, este if corrige este caso.
        n_pags = max(1, n_pags)
        # Verifica se há páginas escondidas.
        if n_pags == 10:
            # Clica em '>> >>'
            interact('click', '//*[@id="servicos_prestados_form:datatable_servico_prestado:j_id614_table"]/tbody/tr/td[16]')
            # Aguarda o carregamento da pesquisa.
            wait.until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="mpProgressoContentTable"]/tbody/tr/td/div')))
            sleep(0.5)
            n_pags = int(nav.find_element('xpath', '//*[@id="servicos_prestados_form:datatable_servico_prestado:j_id614_table"]').text.split()[-3])

        # Clica em 'Encerramento'.
        interact('click', '//*[@id="abaEncerramento_lbl"]')
        for i in range(n_pags):
            # Clica em 'Serviços Prestados'.
            interact('click', '//*[@id="abaServicosPrestados_lbl"]')
            # Clica em 'Pesquisar'.
            interact('click', '//*[@id="servicos_prestados_form:j_id514"]')
            if i < 10:
                # Avança até a página correta.
                interact('click', f'//*[@id="servicos_prestados_form:datatable_servico_prestado:j_id614_table"]/tbody/tr/td[{4+i}]')
            else:
                # Avança até a página 10.
                interact('click',
                         f'//*[@id="servicos_prestados_form:datatable_servico_prestado:j_id614_table"]/tbody/tr/td[{13}]')
                for _ in range(i-9):
                    # Clica em '>>'.
                    interact('click', '//*[@id="servicos_prestados_form:datatable_servico_prestado:j_id614_table"]/tbody/tr/td[15]')
                    # Aguarda o carregamento da pesquisa.
                    wait.until(EC.invisibility_of_element_located(
                        (By.XPATH, '//*[@id="mpProgressoContentTable"]/tbody/tr/td/div')))
                    sleep(0.1)
            # Aguarda o carregamento da página
            sleep(0.1)
            wait.until(EC.element_to_be_clickable(('xpath', '//*[@id="servicos_prestados_form:j_id514"]')))
            sleep(0.5)
            # Conta quantos itens há na página
            n_itens = len(nav.find_element('xpath', '//*[@id="servicos_prestados_form:datatable_servico_prestado:tb"]').text.split('\n'))
            # Clica em 'Encerramento'.
            interact('click', '//*[@id="abaEncerramento_lbl"]')
            for ii in range(n_itens):
                sleep(1)
                # Clica em 'Serviços Prestados'.
                interact('click', '//*[@id="abaServicosPrestados_lbl"]')
                # Clica em 'Pesquisar'.
                interact('click', '//*[@id="servicos_prestados_form:j_id514"]')
                if i < 10:
                    # Avança até a página correta.
                    interact('click',
                             f'//*[@id="servicos_prestados_form:datatable_servico_prestado:j_id614_table"]/tbody/tr/td[{4 + i}]')
                else:
                    # Avança até a página 10.
                    interact('click',
                             f'//*[@id="servicos_prestados_form:datatable_servico_prestado:j_id614_table"]/tbody/tr/td[{13}]')
                    for _ in range(i - 9):
                        # Clica em '>>'.
                        interact('click',
                                 '//*[@id="servicos_prestados_form:datatable_servico_prestado:j_id614_table"]/tbody/tr/td[15]')
                        # Aguarda o carregamento da pesquisa.
                        wait.until(EC.invisibility_of_element_located(
                            (By.XPATH, '//*[@id="mpProgressoContentTable"]/tbody/tr/td/div')))
                        sleep(0.1)
                # Clica no símbolo de lupa.
                interact('click', f'//*[@id="servicos_prestados_form:datatable_servico_prestado:{10*i+ii}:j_id588"]/a/span')
                try:
                    # Clica em 'Exportar PDF'.
                    interact('click', '//*[@id="j_id161:panelAcoes"]/tbody/tr/td[1]/input')
                except Exception:  # Pode acontecer de o clique na lupa não funcionar.
                    # Clica no símbolo de lupa.
                    interact('click', f'//*[@id="servicos_prestados_form:datatable_servico_prestado:{10 * i + ii}:j_id588"]/a/span')
                    # Clica em 'Exportar PDF'.
                    interact('click', '//*[@id="j_id161:panelAcoes"]/tbody/tr/td[1]/input')
                # Clicaq em 'Voltar'.
                interact('click', '//*[@id="j_id161:panelAcoes"]/tbody/tr/td[2]/input')
    sleep(3)  # Aguarda o fim do download da última nota.
    nav.close()


def start_nav():
    # Inicializa o navegador
    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": f'{os.getcwd()}\\notas',
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_setting_values.automatic_downloads": 1
    })
    nav = webdriver.Chrome(service=Service(), options=options)
    wait = WebDriverWait(nav, 30)
    nav.maximize_window()
    return nav, wait


def espera_aparecer(nav, wait, xpath: str, n: int = 10) -> None:
    """
    Espera n segundos até que determinado item esteja na tela.
    :param xpath: Uma string com o xpath do item que se deseja esperar aperecer.
    :param n: O total de segundos que se deseja esperar.
    """
    for _ in range(n):
        if nav.find_elements('xpath', xpath):
            try:
                wait.until(EC.element_to_be_clickable(('xpath', xpath)))
            except TimeoutException:
                continue
            except NoSuchElementException:
                continue
            sleep(0.1)
            return
        sleep(1)
    raise NoSuchElementException(f'{xpath} não encontrado em {n} segundos de espera')


def _interact(nav, wait, action: str, xpath: str, keys: str = None, n_tries: int = 5) -> None:
    """
    Interage com determinado elemento na tela.
    Primeiro chama a função 'espera_aparecer' para não causar erro de Not Found.
    :param xpath: Uma string com o xpath do elemento que se deseja esperar aperecer.
    """
    actions = ['click', 'write', 'clear']
    if action not in actions:
        raise TypeError(f'{action} must be in {actions}')
    espera_aparecer(nav, wait, xpath)
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
        except StaleElementReferenceException:
            sleep(1)
        except ElementClickInterceptedException:
            sleep(1)
        except UnexpectedAlertPresentException:
            try:
                alert = nav.switch_to.alert
                alert.dismiss()  # Recusa o alerta
            except NoAlertPresentException:
                pass
    return xpath


def get_creds() -> Dict:
    # Lê as credenciais de acesso
    with open('config.txt', 'r') as file:
        # Separa o arquivo por linha
        dados = file.read().split('\n')
        # Separa cada chave do seu valor
        dados = [(linha.split('-->')[0], linha.split('-->')[1].strip()) for linha in dados]
        # Cria um dicionário com os valores lidos
        dados = {chave: valor for chave, valor in dados}
        # Converte a data no modelo dd/mm/YYYY para uma variável do tipo datetime
        dados['dia'] = datetime(int(dados['Data'][6:]), int(dados['Data'][3:5]), int(dados['Data'][:2]))
        dados['mes'] = dados['Data'][3:5]
        return dados


def get_modelo_nome(opcao: str) -> str:
    modelos = {
        '1': '{nome} - {num_nf}.pdf',
        '2': 'NF {num_nf} - {nome}.pdf',
        '3': '{nome} - {num_nf} desp nf.pdf'
    }
    modelo = modelos.get(opcao, None)
    if modelo is None:
        print(f'O Modelo deve estar entre os seguintes: {list(modelos.keys())}.')
        input()
        raise TypeError()
    else:
        return modelo


def renomeia_notas(opcao: str):
    print('Renomeando notas...')
    modelo = get_modelo_nome(opcao)

    notas = [nota for nota in os.listdir('notas') if '.pdf' in nota]
    for nota in tqdm(notas):
        arq = f'notas/{nota}'

        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            # Extrai o texto do PDF
            rows = pdf_reader.pages[0].extract_text().split('\n')

        num_nf = rows[4]
        for row in rows:
            if 'Regime especial Tributação' in row:
                nome = row[26:].replace('/', '')
                break
        for row in rows:
            if 'E-mail' in row:
                empresa = row[row.rfind('E-mail') + 6:].replace('/', '')
                break
        nome_nota = modelo.format(num_nf=num_nf, nome=nome)
        # Verifica se ja há uma pasta para esta empresa
        if not os.path.exists(f'notas/{empresa}'):
            os.mkdir(f'notas/{empresa}')
        # Verifica se o arquivo já existe na pasta.
        if not os.path.exists(f'notas/{empresa}/{nome_nota}'):
            # Move o arquivo para a nova pasta
            os.rename(arq, f'notas/{empresa}/{nome_nota}')
        else:
            os.remove(arq)


def atualiza_relatorio() -> None:
    if 'Relatorio.xlsx' not in os.listdir():
        relatorio = pd.DataFrame(columns=['Empresa', 'Número NF', 'Emissão', 'Valor Líquido'])
    else:
        relatorio = pd.read_excel('Relatorio.xlsx')

    files: List[str] = []
    for folder in os.listdir('notas'):
        files += [f'notas/{folder}/{file}'
                  for file in os.listdir(f'notas/{folder}')
                  if '.pdf' in file]

    for file in files:
    
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b)
            # Cada nota só tem uma página
            rows = pdf.pages[0].extract_text().split('\n')

        empresa = file[file.find('/')+1:file.rfind('/')]
        num_nf = rows[4]
        for row in rows:
            if 'Local da Prestação' in row:
                emissao = row[18:].split()[0]
                break
        for row in rows:
            if 'Código ART' in row:
                valor = row[:-10]
                break

        relatorio.loc[len(relatorio)] = [empresa, num_nf, emissao, valor]
    relatorio.to_excel('Relatorio.xlsx', index=False)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        input()
