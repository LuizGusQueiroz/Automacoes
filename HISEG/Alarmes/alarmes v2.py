# parte única
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from datetime import date, timedelta
from selenium import webdriver
from time import sleep
from sys import exit
import pandas as pd
import shutil
import os


class Automacao:
    def __init__(self, email: str, senha: str, meses_para_baixar: int = 12):
        self.email = email
        self.senha = senha
        self.lista_datas = []
        self.intervalo = meses_para_baixar
        self.init_lista_datas()
        self.pasta_download = r'C:\Users\ADM\Downloads'
        self.pasta_destino = r'C:\Users\ADM\OneDrive - KMF - CONSULTORIA EMPRESARIAL E TREINAMENTOS LTDA - ME\HISEG - Sharepoint\somaseg_ordensServico'
        options = Options()
        options.add_experimental_option('prefs', {
            "download.default_directory": self.pasta_download,  # Pasta de download.
            "download.prompt_for_download": False,  # Desativa o prompt de download.
            "download.directory_upgrade": True,  # Atualiza a pasta de download sem prompt.
            "safebrowsing.enabled": True  # Ativa a segurança de navegação.
        })
        # Inicializa o navegador.
        self.nav = webdriver.Edge(service=Service(), options=options)
        self.wait = WebDriverWait(self.nav, 30)
        self.nav.maximize_window()

    def espera_aparecer(self, xpath: str, by, n: int = 20):
        """
        Espera n segundos até que determinado item esteja na tela.
        :param xpath: Uma string com o xpath do item que se deseja esperar aperecer.
        :param n: O total de segundos que se deseja esperar.
        """
        for _ in range(n):
            if self.nav.find_elements(by, xpath):
                try:
                    self.wait.until(EC.element_to_be_clickable((by, xpath)))
                except TimeoutException:
                    continue
                except NoSuchElementException:
                    continue
                sleep(0.1)
                return
            sleep(1)
        raise NoSuchElementException(f'{xpath} não encontrado em {n} segundos de espera')

    def interact(self, action: str, xpath: str, keys: str = '', by=By.XPATH, n_tries: int = 5):
        """
        Interage com determinado elemento na tela.
        Primeiro chama a função 'espera_aparecer' para não causar erro de Not Found.
        :param action: Ação que se deseja realizar.
        :param xpath: Uma string com o xpath do elemento que se deseja esperar aperecer.
        :param keys: Uma string que é o texto que se deseja escrever.
        :param by: Tipo de tag que será buscado, By.XPATH, By.ID, ...
        :param n_tries: A tolerância do número de tentativas da ação.
        """
        actions = ['click', 'write', 'clear']
        if action not in actions:
            raise TypeError(f'{action} must be in {actions}')
        self.espera_aparecer(xpath, by)
        for try_i in range(n_tries):
            try:
                # Find the element.
                element = self.nav.find_element(by, xpath)
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

    def click(self, xpath, by=By.XPATH):
        self.interact('click', xpath, by)

    def write(self, xpath, keys='', by=By.XPATH):
        self.interact('write', xpath, keys, by)

    def clear(self, xpath, by=By.XPATH):
        self.interact('clear', xpath, by)

    def init_lista_datas(self):
        ontem = (date.today() - timedelta(days=1))
        data_min = (ontem - timedelta(days=365)).replace(day=1)
        #data_min = date(2025, 3, 1)  # date(data_min.year, data_min.month, 1)
        # data_min = date(data_min.year, 2, 1)
        if data_min < date(2024, 1, 1):
            data_min = date(2024, 1, 1)

        #self.intervalo = (ontem.year - data_min.year) * 12 + (ontem.month - data_min.month)

        for i in range(self.intervalo, 0, -1):
            # Data inicial do intervalo
            inicio = data_min.replace(month=((data_min.month + i - 1) % 12) + 1,
                                      year=data_min.year + ((data_min.month + i - 1) // 12))

            # Data final do intervalo
            proximo_mes = inicio.replace(day=28) + timedelta(days=4)  # Vai para o próximo mês
            data_max = proximo_mes.replace(day=1) - timedelta(days=1)  # Último dia do mês atual
            if data_max > ontem:
                data_max = ontem

            # Formata as datas no formato DDMMYYYY
            minimo = inicio.strftime('%d%m%Y')
            maximo = data_max.strftime('%d%m%Y')

            self.lista_datas.append([minimo, maximo])

    def esperar_download(self, timeout=240):
        espera = 0
        while True:
            arquivos = os.listdir(self.pasta_download)
            if any(arquivo.endswith('.xls') for arquivo in arquivos):
                sleep(2)
                return
            sleep(1)
            espera += 1
            if espera > timeout:
                raise Exception("Tempo esgotado esperando pelo download do arquivo.")

    def converte_para_csv(self, data_inicial, data_final):
        for file in os.listdir(self.pasta_download):
            if file.endswith('.xls'):
                file_name = f'ordensServico_{data_inicial[-4:]}.{data_inicial[2:4]}'
                xls_file_name = f'{file_name}.xls'
                shutil.move(os.path.join(self.pasta_download, file), os.path.join(self.pasta_destino, xls_file_name))
                xls_file = os.path.join(self.pasta_destino, xls_file_name)

                xlsx_file_name = f'{file_name}.xlsx'
                xlsx_file = os.path.join(self.pasta_destino, xlsx_file_name)

                csv_file_name = f'{file_name}.csv'
                csv_file = os.path.join(self.pasta_destino, csv_file_name)

                if os.path.exists(xlsx_file):
                    os.remove(xlsx_file)

                sleep(0.5)
                df = pd.read_html(xls_file)[0]

                if os.path.exists(csv_file):
                    os.remove(csv_file)

                df.to_csv(csv_file, index=False)
                os.remove(xls_file)

    def run(self):
        self.login()
        self.baixa_relatorios()

    def login(self):
        self.nav.get('https://www.somaseg.com.br/user/login')
        # Clica em 'Login'.
        self.click('/html/body/header/div[2]/button/span')
        # Preenche o email e senha.
        self.write('//*[@id="email"]', self.email)
        self.write('//*[@id="senha"]', self.senha)
        # Clica em 'Entrar'.
        self.click('/html/body/div[1]/div/div[2]/form/div[3]/button')

    def baixa_relatorios(self):
        # Clica em 'Serviços'.
        self.click('/html/body/nav/section/ul/li[13]/a/span')
        #
        for i in range(self.intervalo):
            data_inicial = self.lista_datas[i][0]
            data_final = self.lista_datas[i][1]
            # Limpa e preenche o campo Data inicial.
            self.clear('//*[@id="data-inicial"]')
            self.write('//*[@id="data-inicial"]', data_inicial)
            # Limpa e preenche o campo Data Final.
            self.clear('//*[@id="data-final"]')
            self.write('//*[@id="data-final"]', data_final)
            # Clica em 'Pesquisar'.
            self.click('//*[@id="form-search"]/div[9]/div/div/button[1]')
            # Clica em 'Gerar planilha'.
            self.click('//*[@id="contentlayout"]/section[1]/div[2]/div/button[2]')
            # Marca a caixa 'Mostrar atividades dos técnicos'.
            self.click('/html/body/div[7]/form/div[1]/content/label/input')
            # Clica em 'Gerar'.
            self.click('//*[@id="div-buttonsModalJS"]/div/div/button[1]')
            print(f"Executando download do arquivo de Ordens de Serviço no período de {data_inicial} até {data_final}")
            self.esperar_download()
            print('Download concluído!')
            print('\n')
            self.converte_para_csv(data_inicial, data_final)



try:
    email = 'email'
    senha = 'senha'
    aut = Automacao(email, senha)
    aut.run()

except Exception as e:
    print(e)
