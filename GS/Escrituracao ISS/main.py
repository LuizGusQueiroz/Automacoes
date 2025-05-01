from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium import webdriver
from time import sleep
import os


class Escriturador:
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

    def write(self, xpath, keys):
        self.interact('write', xpath, keys)

    def clear(self, xpath):
        self.interact('clear', xpath)

    def run(self):
        self.nav.get('https://iss.fortaleza.ce.gov.br/grpfor/login.seam;jsessionid=XlNA4Q88SBUd7BNCIPsZwC6h.carina:iss-prod-04?cid=100967')
        self.login()
        self.seleciona_inscricao()
        self.emite_nf('15741787000110')
        sleep(50)

    def login(self):
        """
        Passa pela tela de login do site.
        """
        # Aguarda o site carregar
        sleep(1)
        # Clica em 'Login'.
        self.click('//*[@id="login"]/div[1]/div/a[1]')
        sleep(1)
        # Verifica se está na página de Login
        while self.nav.find_elements('xpath', '//*[@id="botao-entrar"]'):
            # Preenche as informações de Login
            self.clear('//*[@id="username"]')  # Limpa o login atual
            self.write('//*[@id="username"]', self.creds['LOGIN'])
            self.clear('//*[@id="password"]')  # Limpa a senha atual
            self.write('//*[@id="password"]', self.creds['SENHA'])
            # Clica em entrar
            self.click('//*[@id="botao-entrar"]')
            sleep(1)
        # Aguarda o carregamento da página
        sleep(2)

    def seleciona_inscricao(self):
        """
        Escolhe a inscrição desejada dentre a tabela de inscrições.
        """
        achou: bool = False
        # Verifica se a tabela de CNPJ existe.
        if not self.nav.find_elements('xpath', '//*[@id="alteraInscricaoForm:empresaDataTable"]'):
            return  # Caso não exista, só há uma inscrição que já está selecionada.
        # Conta quantas páginas de CNPJ existem
        if self.nav.find_elements('xpath', '//*[@id="alteraInscricaoForm:empresaDataTable:j_id383_table"]'):
            try:
                n_pags = int(self.nav.find_element(
                    'xpath', '//*[@id="alteraInscricaoForm:empresaDataTable:j_id383_table"]').text.split()[-2])
            except:
                n_pags = 10
        else:
            n_pags = 1
        for pag in range(n_pags):
            sleep(3)  # Extrai os cnpjs a partir de uma tabela
            cnpjs = self.nav.find_element('xpath', '//*[@id="alteraInscricaoForm"]').text.split('\n')
            cnpjs = cnpjs[5::3]

            achou = False
            for i, cnpj in enumerate(cnpjs):
                cnpj_num = ''.join([c for c in cnpj if c.isnumeric()])

                if cnpj == self.creds['CNPJ'] or cnpj_num == self.creds['CNPJ']:
                    achou = True
                    self.click(f'//*[@id="alteraInscricaoForm:empresaDataTable:{10 * pag + i}:linkDocumento"]')
                    # Aguarda o carregamento da página
                    sleep(0.5)
                    break
            if achou:
                break
            # Avança para a próxima página
            if pag != n_pags - 1:
                self.click(f'//*[@id="alteraInscricaoForm:empresaDataTable:j_id383_table"]/tbody/tr/td[{5 + pag}]')

        if not achou:
            raise ValueError(f'CNPJ {self.creds['CNPJ']} não encontrado!')

    def emite_nf(self, cnpj: str, descricao: str, valor: str):
        """
        Realiza a emissão das notas fiscais
        """
        # Clica em 'NFS-e'.
        self.click('//*[@id="navbar"]/ul/li[5]/a')
        # Clica em 'Emitir NFS-e'.
        self.click('//*[@id="formMenuTopo:menuNfse:j_id53"]')
        # Clica em CNPJ.
        self.click('//*[@id="emitirnfseForm:tipoPesquisaTomadorRb:1"]')
        # Aguarda o carregamento.
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="emitirnfseForm:cpfPesquisaTomador"]')))
        sleep(0.5)
        # Digita o CNPJ.
        self.click('//*[@id="emitirnfseForm:cpfPesquisaTomador"]')
        sleep(0.5)
        self.write('//*[@id="emitirnfseForm:cpfPesquisaTomador"]', cnpj)
        # Aguarda o carregamento.
        sleep(1)
        # Acessa a lista de resultados, se for diferente de 1, indica que algo está errado.
        result = self.nav.find_element('xpath', '//*[@id="emitirnfseForm:j_id189:suggest"]').text.split('\n')
        if len(result) != 1:
            raise ValueError(f'Problema com o CNPJ: {cnpj}')
        # Se chegar aqui, há apenas um resultado, que está correto.
        # Dá um enter.
        self.write('//*[@id="emitirnfseForm:cpfPesquisaTomador"]', Keys.RETURN)
        # CLica em 'Serviço'.
        self.click('//*[@id="emitirnfseForm:abaServico_lbl"]')
        # Escolher competência
        # ====================
        # Preencher o CNAE (selecionando entre os disponíveis ou pesquisando pelo código)
        # ===============
        # Preenche o campo 'Descrição do Serviço*:'.
        self.write('//*[@id="emitirnfseForm:idDescricaoServico"]', descricao)
        # Preenche o campo 'Valor do Serviço*:'.
        self.write('//*[@id="emitirnfseForm:idValorServicoPrestado"]', valor)
        # Clica em 'Validar Campos Obrigatórios da NFS-e'.
        # self.click('//*[@id="emitirnfseForm:btnCalcular"]')


if __name__ == '__main__':
    escriturador = Escriturador()
    escriturador.run()
