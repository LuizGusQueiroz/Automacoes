from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium import webdriver
from PyPDF2 import PdfReader
from time import sleep
from PIL import Image
import pyautogui
import base64
import sys
import os


class Automacao:
    def __init__(self):
        # Define a pasta padrão de downloads.
        options = Options()
        options.add_experimental_option('prefs', {
            "download.default_directory": os.getcwd(),  # Pasta de download.
            "download.prompt_for_download": False,  # Desativa o prompt de download.
            "download.directory_upgrade": True,  # Atualiza a pasta de download sem prompt.
            "safebrowsing.enabled": True  # Ativa a segurança de navegação.
        })
        # Inicializa o navegador.
        self.nav = webdriver.Edge(service=Service(), options=options)
        self.wait = WebDriverWait(self.nav, 30)
        self.nav.maximize_window()
        self.creds = self.get_creds()

    def get_creds(self):
        # Lê as credenciais de acesso.
        with open('config.txt', 'r') as file:
            # Separa o arquivo por linha.
            creds = file.read().split('\n')
            # Separa cada chave do seu valor.
            creds = [(linha.split('-->')[0], linha.split('-->')[1].strip()) for linha in creds]
            # Retorna um dicionário com os valores lidos.
            return {chave: valor for chave, valor in creds}

    def espera_aparecer(self, xpath: str, n: int = 20):
        """
        Espera n segundos até que determinado item esteja na tela.
        :param xpath: Uma string com o xpath do item que se deseja esperar aperecer.
        :param n: O total de segundos que se deseja esperar.
        """
        for _ in range(n):
            if self.nav.find_elements('xpath', xpath):
                try:
                    self.wait.until(EC.element_to_be_clickable(('xpath', xpath)))
                except TimeoutException:
                    continue
                except NoSuchElementException:
                    continue
                sleep(0.1)
                return
            sleep(1)
        raise NoSuchElementException(f'{xpath} não encontrado em {n} segundos de espera')

    def interact(self, action: str, xpath: str, keys: str = '', n_tries: int = 5):
        """
        Interage com determinado elemento na tela.
        Primeiro chama a função 'espera_aparecer' para não causar erro de Not Found.
        :param action: Ação que se deseja realizar.
        :param xpath: Uma string com o xpath do elemento que se deseja esperar aperecer.
        :param keys: Uma string que é o texto que se deseja escrever.
        :param n_tries: A tolerância do número de tentativas da ação.
        """
        actions = ['click', 'write', 'clear']
        if action not in actions:
            raise TypeError(f'{action} must be in {actions}')
        self.espera_aparecer(xpath)
        for try_i in range(n_tries):
            try:
                # Find the element.
                element = self.nav.find_element('xpath', xpath)
                # Choose the right action to do.
                if action == 'click':
                    element.click()
                elif action == 'write':
                    element.send_keys(keys)
                elif action == 'clear':
                    element.clear()
                return
            except Exception:
                sleep(1)

    def click(self, xpath):
        self.interact('click', xpath)

    def write(self, xpath, keys=''):
        self.interact('write', xpath, keys)

    def clear(self, xpath):
        self.interact('clear', xpath)

    def run(self):
        self.init_dir()
        self.login()
        self.download_relatorio()
        self.get_nomes()
        self.get_links()
        self.download_nfs()
        sleep(3)
        self.nav.close()

    def init_dir(self):
        if not os.path.exists('Notas'):
            os.mkdir('Notas')

    def login(self):
        """
        Passa pela tela de login do site.
        """
        # Acessa o site.
        self.nav.get('https://isscuritiba.curitiba.pr.gov.br/iss/default.aspx')
        # Aguarda o site carregar
        sleep(3)
        self.main_window = self.nav.current_window_handle

        # Encontrar o identificador da nova janela.
        for window in self.nav.window_handles:
            if window != self.main_window:
                self.sec_window = window
                self.nav.switch_to.window(self.sec_window)
                break

        # Verifica se há um aviso na tela inicial, caso haja, clica em 'Fechar'.
        if self.nav.find_elements(By.XPATH, '//*[@id="btnFechar"]'):
            self.click('//*[@id="btnFechar"]')

        while self.nav.find_elements('xpath', '//*[@id="btnLogar"]'):
            # Limpa o campo de login.
            self.clear('//*[@id="txtLogin"]')
            # Preenche o campo login.
            self.write('//*[@id="txtLogin"]', self.creds['LOGIN'])
            # Preenche o campo senha.
            self.write('//*[@id="txtSenha"]', self.creds['SENHA'])
            # Acessa a caixa do captcha.
            self.write('//*[@id="txtCodeTextBox"]', '')
            sleep(7)
            # Clica em 'Entrar'.
            self.click('//*[@id="btnLogar"]')
            # Alternar para a nova janela
        sleep(1)

    def download_relatorio(self):
        """
        Baixo o relatório de notas fiscais.
        """
        self.wait.until(EC.frame_to_be_available_and_switch_to_it(('xpath', '//*[@id="fraMenu"]')))
        # Clica em 'NFS-e'
        self.click('//*[@id="td1_div5"]/b/span')
        # Volta para o contexto do frame pai.
        self.nav.switch_to.default_content()
        self.wait.until(EC.frame_to_be_available_and_switch_to_it(('xpath', '//*[@id="fraMain"]')))
        self.wait.until(EC.frame_to_be_available_and_switch_to_it(('xpath', '//*[@id="iFrameMenu"]')))
        # Clica em 'Pesquisar NFS-e emitidas/Cancelar NFS-e'
        self.click('//*[@id="form1"]/div[2]/table/tbody/tr/td/div[3]/a')
        # Volta para o contexto do frame pai.
        self.nav.switch_to.default_content()
        self.wait.until(EC.frame_to_be_available_and_switch_to_it(('xpath', '//*[@id="fraMain"]')))
        self.wait.until(
            EC.frame_to_be_available_and_switch_to_it(('xpath', '//*[@id="ctl00_ContentPlaceHolder1_frmObras"]')))
        # Escolhe a competência desejada.
        Select(self.nav.find_element('xpath', '//*[@id="Mes"]')).select_by_visible_text(self.creds['Competencia'])
        # Clica em 'Pesquisar'
        self.click('//*[@id="btnPesquisar"]')
        # Clica em 'Gerar Relatório'.
        self.click('//*[@id="btnContainerNfse"]/div/a[3]')
        sleep(2)
        # Clica fora da tela aberta, para fecha-la.
        pyautogui.moveTo(50, 300)
        pyautogui.click()
        # Verifica se o Pdf foi baixado.
        if not [file for file in os.listdir() if '.pdf' in file.lower()]:
            # Clica em 'Gerar Relatório'.
            self.click('//*[@id="btnContainerNfse"]/div/a[3]')
            sleep(2)
            # Clica fora da tela aberta, para fecha-la.
            pyautogui.moveTo(50, 300)
            pyautogui.click()
        # Clica em 'Gerar Links NFS-e'.
        self.click('//*[@id="btnContainerNfse"]/div/a[2]')
        sleep(1)
        # Verifica se o txt foi baixado.
        if len([file for file in os.listdir() if '.txt' in file.lower()]) == 1:
            # Clica fora da tela aberta, para fecha-la.
            pyautogui.moveTo(50, 300)
            pyautogui.click()
            # Clica em 'Gerar Links NFS-e'.
            self.click('//*[@id="btnContainerNfse"]/div/a[2]')
            sleep(1)



    def get_nomes(self) -> None:
        """
        Guarda um dicionário que contém a relação de número NF -> nome condomínio.
        Obtida a partir do relatório Pdf baixado.
        """
        nomes = {}
        rel_pdf = [file for file in os.listdir() if '.pdf' in file.lower()][0]
        with open(rel_pdf, 'rb') as file:
            rows = PdfReader(file).pages[0].extract_text().split('\n')
            i = 0
            while rows[i] != ' Número':
                i += 1
            while rows[i + 1] != ' Página:':
                i += 1
                nome = rows[i][1:]
                while not rows[i][1:].isnumeric():
                    i += 1
                nomes[rows[i][1:]] = nome
        self.nomes = nomes
        os.remove(rel_pdf)

    def get_links(self) -> None:
        """
        Guarda um dicionário que contém a relação Num NF -> link para dowloado.
        Obtida a partir do relatório txt baixado.
        """
        rel_txt = [file for file in os.listdir() if '.txt' in file.lower() and file not in ['config.txt']][0]
        with open(rel_txt, 'r') as file:
            # Realiza a leitura do arquivo txt e quebra por linha.
            arq = file.read().split('\n')
            # Separa cada linha por espaço e guarda apenas as linhas com mais que 3 itens.
            rows = [row.split() for row in arq if len(row.split()) > 3]
            rows = [{'num_nf': row[-1], 'link': 'https://'+row[-2]} for row in rows]
            self.links = rows
        os.remove(rel_txt)

    def salva_img(self, num_nf: str):
        """
        Salva a imagem da nota fiscal exibida na tela.
        """
        # Acessa o elemento imagem.
        img_element = WebDriverWait(self.nav, 10).until(
            EC.presence_of_element_located(('xpath', '//*[@id="Impressao"]')))
        # Obtém o atributo 'src' que contém a imagem codificada em base64.
        img_data = img_element.get_attribute('src')
        # Remove o prefixo da string base64.
        img_data = img_data.split(',')[1]
        # Decodifica a imagem base64.
        img_bytes = base64.b64decode(img_data)
        # Salva a imagem.
        with open('Notas/nf.jpg', 'wb') as file:
            file.write(img_bytes)
        # Nome do arquivo que será salvo. Está no modelo nome_condominio-num_nf.pdf.
        nome = f'Notas/{self.nomes[num_nf]}-{num_nf}.pdf'
        # Abre a imagem salva, a redimensiona e salva como pdf.
        Image.open('Notas/nf.jpg').resize((710, 950)).convert('RGB').save(nome)

    def download_nfs(self):
        """
        Realiza o download de todas as notas fiscais disponíveis a partir
        do dicionário de links obtido.
        """
        for row in self.links:
            self.nav.get(row['link'])
            self.salva_img(row['num_nf'])
        # Apaga a última imagem baixada.
        os.remove('Notas/nf.jpg')


if __name__ == '__main__':
    try:
        aut = Automacao()
        aut.run()
    except:
        # Apaga arquivos pdf e txt que restaram.
        files = [file for file in os.listdir()
                 if ('.pdf' in file.lower() or '.txt' in file.lower())
                 and file not in ['config.txt']]
    sys.exit()
