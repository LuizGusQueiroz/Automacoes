# parte única
import time
import os
import shutil
import requests as req
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from datetime import date, timedelta
import win32com.client as win32
import win32com
import pythoncom
import traceback


# def reparar_e_converter_xls(file_path_xls, file_path_xlsx):
#    try:
# Regenerar arquivos makepy para o Excel
#        pythoncom.CoInitialize()
#        module = win32.gencache.EnsureModule('{00020813-0000-0000-C000-000000000046}', 0, 1, 8)

#        excel = win32.gencache.EnsureDispatch('Excel.Application')
#        excel = win32com.client.Dispatch("Excel.Application") #aplicados dia 27/01/2025
#        excel.Visible = False  # Configura invisibilidade #aplicados dia 27/01/2025
#        time.sleep(1)
#        wb = excel.Workbooks.Open(file_path_xls)

# Salvar como um novo arquivo Excel
#        wb.SaveAs(file_path_xlsx, FileFormat=51)  # 51 é o formato para .xlsx
#        wb.Close()
#        excel.Application.Quit()
#        pythoncom.CoUninitialize()
#    except Exception as e:
#        print("Erro ao converter arquivo XLS para XLSX:")
#        print(traceback.format_exc())
#        pythoncom.CoUninitialize()
#        raise
# tentativa 2

# tentativa 3
def reparar_e_converter_xls(file_path_xls, file_path_xlsx):
    excel = None
    wb = None
    try:
        # Limpa o cache do win32com
        clear_win32com_cache()

        # Inicializa o COM
        pythoncom.CoInitialize()

        # Abre o Excel
        excel = win32com.client.Dispatch('Excel.Application')
        excel.Visible = False
        excel.DisplayAlerts = False

        # Abre o arquivo XLS
        time.sleep(5)
        wb = excel.Workbooks.Open(file_path_xls)
        time.sleep(2)

        # Salva como XLSX
        wb.SaveAs(file_path_xlsx, FileFormat=51)  # 51 é o formato para .xlsx
        wb.Close()

    except Exception as e:
        print("Erro ao converter arquivo XLS para XLSX:")
        print(traceback.format_exc())
        raise
    finally:
        # Fecha o Excel e libera os objetos COM
        if wb is not None:
            try:
                wb.Close(SaveChanges=False)  # Fecha sem salvar alterações
            except Exception as e:
                print("Erro ao fechar o Workbook:", e)
        if excel is not None:
            try:
                excel.Quit()
            except Exception as e:
                print("Erro ao fechar o Excel:", e)
        pythoncom.CoUninitialize()


def esperar_download(pasta_download, timeout=240):
    espera = 0
    while True:
        arquivos = os.listdir(pasta_download)
        if any(arquivo.endswith('.xls') for arquivo in arquivos):
            time.sleep(2)
            return
        time.sleep(1)
        espera += 1
        if espera > timeout:
            raise Exception("Tempo esgotado esperando pelo download do arquivo.")


# Limpar cache do win32com
def clear_win32com_cache():
    import site
    gen_py_path = os.path.join(site.getsitepackages()[0], 'win32com', 'gen_py')
    if not os.path.exists(gen_py_path):
        os.makedirs(gen_py_path)
    try:
        shutil.rmtree(gen_py_path)
        print("Cache do win32com limpo com sucesso.")
    except Exception as e:
        print(f"Erro ao limpar cache do win32com: {e}")


clear_win32com_cache()

# makepy_output = win32.gencache.EnsureModule('{00020813-0000-0000-C000-000000000046}', 0, 1, 8)
url = 'https://www.somaseg.com.br/user/login'
email = ''
senha = ''

pasta_download = r'C:\Users\ADM\Downloads'
pasta_destino = r'C:\Users\ADM\OneDrive - KMF - CONSULTORIA EMPRESARIAL E TREINAMENTOS LTDA - ME\HISEG - Sharepoint\somaseg_ordensServico'
pasta_download = r'C:\Users\Usuario\Downloads'
pasta_destino = f'{os.getcwd()}/Ds'
options = webdriver.ChromeOptions()
prefs = {'download.default_directory': pasta_download}
options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome()
driver.get(url)
# driver.set_window_size(1024, 600)
driver.maximize_window()
wait = WebDriverWait(driver, 10)

# Logar no Somaseg

botao_login = wait.until(
    EC.element_to_be_clickable(driver.find_element(By.XPATH, '/html/body/header/div[2]/button/span'))).click()

login = wait.until(EC.element_to_be_clickable(driver.find_element(By.ID, 'email')))
login.send_keys(email)

campo_senha = wait.until(EC.element_to_be_clickable(driver.find_element(By.XPATH, '//*[@id="senha"]')))

campo_senha.click()
campo_senha.send_keys(senha)

botao_login_2 = wait.until(
    EC.element_to_be_clickable(driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/form/div[3]/button')))
botao_login_2.click()

# Entrar na página "Ordens de Serviço"
time.sleep(3)
navegacao = driver.find_elements(By.TAG_NAME, 'a')

for botoes in navegacao:
    # print(botoes.get_attribute('title'))
    if botoes.get_attribute('title') == 'Serviços':  # 'Ordem de serviço':
        botao_entrar_os = botoes
        botao_entrar_os.click()
        break

ontem = (date.today() - timedelta(days=1))
data_min = ontem - timedelta(days=365)
data_min = date(data_min.year, data_min.month, 1)
# data_min = date(data_min.year, 2, 1)
if data_min < date(2024, 1, 1):
    data_min = date(2024, 1, 1)

intervalo = (ontem.year - data_min.year) * 12 + (ontem.month - data_min.month)

lista_datas = []

for i in range(intervalo + 1):
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

    lista_datas.append([minimo, maximo])

for i in range(intervalo + 1):
    data_inicial = lista_datas[i][0]
    data_final = lista_datas[i][1]

    campo_data_inicial = wait.until(EC.element_to_be_clickable(driver.find_element(By.ID, 'data-inicial')))
    campo_data_inicial.clear()
    campo_data_inicial.click()
    campo_data_inicial.send_keys(data_inicial)

    campo_data_final = wait.until(EC.element_to_be_clickable(driver.find_element(By.NAME, 'data_final')))
    campo_data_final.clear()
    campo_data_final.click()
    campo_data_final.send_keys(data_final)

    botoes_os = driver.find_elements(By.TAG_NAME, 'button')
    for botao_os in botoes_os:
        if botao_os.text == 'Pesquisar':
            driver.execute_script("arguments[0].scrollIntoView();", botao_os)
            botao_os.click()
            break
    time.sleep(1)
    botoes_relatorio = driver.find_elements(By.TAG_NAME, 'button')
    for botao_relatorio in botoes_relatorio:
        time.sleep(1)
        # print(botao_relatorio.text.strip())
        if botao_relatorio.text == 'Gerar planilha' or botao_relatorio.text == ' Gerar planilha':
            driver.execute_script("arguments[0].scrollIntoView();", botao_relatorio)
            botao_relatorio.click()
            break

    caixa_logs = wait.until(EC.element_to_be_clickable(driver.find_element(By.NAME, 'mostrar-atividades-tecnicos')))
    caixa_logs.click()

    botoes_export = driver.find_elements(By.TAG_NAME, 'button')
    for botao_export in botoes_export:
        if botao_export.text == 'Gerar':
            botao_export.click()
            break
    print(f"Executando download do arquivo de Ordens de Serviço no período de {data_inicial} até {data_final}")
    esperar_download(pasta_download)
    print('Download concluído!')
    print('\n')

    for file in os.listdir(pasta_download):
        if file.endswith('.xls'):
            file_name = f'ordensServico_{data_inicial[-4:]}.{data_inicial[2:4]}'
            xls_file_name = f'{file_name}.xls'
            shutil.move(os.path.join(pasta_download, file), os.path.join(pasta_destino, xls_file_name))
            xls_file = os.path.join(pasta_destino, xls_file_name)

            xlsx_file_name = f'{file_name}.xlsx'
            xlsx_file = os.path.join(pasta_destino, xlsx_file_name)

            csv_file_name = f'{file_name}.csv'
            csv_file = os.path.join(pasta_destino, csv_file_name)

            if os.path.exists(xlsx_file):
                os.remove(xlsx_file)

            time.sleep(0.5)
            reparar_e_converter_xls(xls_file, xlsx_file)
            df = pd.read_excel(xlsx_file)

            if os.path.exists(csv_file):
                os.remove(csv_file)

            df.to_csv(csv_file, index=False)
            os.remove(xls_file)
            os.remove(xlsx_file)

driver.quit()
print("Bases exportadas e direcionadas para o Sharepoint com sucesso!")