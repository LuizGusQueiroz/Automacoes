from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium import webdriver
from typing import List
from time import sleep
from PIL import Image
import requests
import os


class Automacao:
    def __init__(self):
        # Inicializa o navegador.
        self.nav = webdriver.Edge(service=Service())
        self.wait = WebDriverWait(self.nav, 30)
        self.nav.maximize_window()
        # Lê as credenciais de acesso.
        with open('config.txt', 'r') as file:
            # Separa o arquivo por linha.
            creds = file.read().split('\n')
            # Separa cada chave do seu valor.
            creds = [(linha.split('-->')[0], linha.split('-->')[1].strip()) for linha in creds]
        # Guarda um dicionário com os valores lidos.
        self.creds = {chave: valor for chave, valor in creds}

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
        self.go_to_nfs_page()
        self.download_nfs()
        sleep(50)

    def init_dir(self):
        if not os.path.exists('Notas'):
            os.mkdir('Notas')

    def login(self):
        """
        Passa pela tela de login do site.
        """
        # Acessa o site.
        self.nav.get('https://nfse.salvador.ba.gov.br/')
        # Aguarda o site carregar
        sleep(1)
        # Preenche o campo 'Digite seu CPF ou CNPJ.
        self.write('//*[@id="txtLogin"]', self.creds['LOGIN'])
        # Preenche o campo 'Digite sua Senha'.
        self.write('//*[@id="txtSenha"]', self.creds['SENHA'])
        # Acessa o campo do Captcha.
        self.write('//*[@id="tbCaptcha"]')
        # Aguarda o captcha ser preenchido e a tela ser trocada.
        while self.nav.find_elements('xpath', '//*[@id="txtLogin"]'):
            sleep(1)
        # Aguarda o carregamento da página.
        sleep(2)
        # Volta para a página anterior, pois desta forma, a página do gov.br é pulada.
        self.nav.back()
        sleep(1)
        # Pode acontecer de a senha sumir, então é necessário limpar o campo e digitar a senha novamente.
        self.clear('//*[@id="txtSenha"]')
        self.write('//*[@id="txtSenha"]', self.creds['SENHA'])
        # Clica em 'Acessar'.
        self.click('//*[@id="cmdLogin"]')
        # Aguarda o carregamento da página.
        sleep(2)

    def salva_img(self, row: List[str]):
        """
        Salva a imagem da nota fiscal exibida na tela.
        """
        # Acessa o elemento imagem.
        img_element = WebDriverWait(self.nav, 10).until(
            EC.presence_of_element_located(('xpath', '//*[@id="img"]')))
        # Faz o download da imagem a partir da URL do elemento.
        img_response = requests.get(img_element.get_attribute('src'))
        # Salva a imagem.
        with open('Notas/nf.jpg', 'wb') as file:
            file.write(img_response.content)
        # Nome do arquivo que será salvo. Está no modelo nome_condominio-num_nf.pdf.
        nome = f'Notas/{' '.join(row[5:])}-{row[0]}.pdf'
        # Abre a imagem salva, a redimensiona e salva como pdf.
        Image.open('Notas/nf.jpg').resize((1140, 1330)).convert('RGB').save(nome)

    def go_to_nfs_page(self):
        """
        Vai até a página onde se pode baixar as notas fiscais.
        """
        # Caso haja um informativo, clica em 'Acessar Nota Salvador'.
        if self.nav.find_elements(By.XPATH, '//*[@id="pnPopUpMsg"]/div/div[1]/span/a'):
            self.click('//*[@id="pnPopUpMsg"]/div/div[1]/span/a')
        # Clica em 'Consultar NFS-e'.
        self.click('//*[@id="menu-lateral"]/li[4]/a')
        # Seleciona a competência desejada.
        Select(self.nav.find_element('xpath', '//*[@id="ddlMes"]')).select_by_visible_text(self.creds['Competencia'])
        # Clica em 'NFS-e Emitidas'
        self.click('//*[@id="btEmitidas"]')

    def download_nfs(self):
        """
        Realiza o download de todas as notas fiscais disponíveis.
        """
        # Guarda a referência da janela principal
        main_window = self.nav.current_window_handle
        # Encontrar o identificador da nova janela aberta.
        for window in self.nav.window_handles:
            if window != main_window:
                sec_window = window
                # Muda o contexto para a janela com a lista de notas.
                self.nav.switch_to.window(sec_window)
                break
        # Acessa os dados da tabela de notas
        notas = self.nav.find_element('xpath', '//*[@id="dgNotas"]').text.split('\n')[2:-1]
        # Pega nota sim, nota não, pois as informações de cada nota estão divididas em duas linhas,
        # mas a segunda linha não tem informações necessárias para esta aplicação.
        notas = [nota for i, nota in enumerate(notas) if i % 2 == 0]
        for i, row in enumerate(notas):
            # Separa o conteúdo da linha.
            row = row.split()
            # Clica no link da nota.
            self.click(f'//*[@id="dgNotas"]/tbody/tr[{i + 2}]/td[1]/a')
            # É aberta uma tela na janela principal
            # Encontrar o identificador da nova janela.
            for window in self.nav.window_handles:
                if window not in [main_window, sec_window]:
                    # Muda o contexto para a janela com a imagem da nota.
                    self.nav.switch_to.window(window)
                    break

            # Salva a imagem da nota fiscal.
            self.salva_img(row)
            # Fecha a janela aberta.
            self.nav.close()
            # Muda para o contexto da janela com a lista de notas.
            self.nav.switch_to.window(sec_window)
        # Apaga a última imagem baixada.
        os.remove('Notas/nf.jpg')


if __name__ == '__main__':
    aut = Automacao()
    aut.run()
