from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime
from typing import List
from tqdm import tqdm
import pandas as pd
import openpyxl
import requests
import json
import time
import os


# ===================================================================
#                             Menus e Configurações
# ===================================================================

VERSION: str = '0.6.1'

main_msg: str = '''
 0: Ajuda (Informações) 
 1: Documentos de Admissão 
 2: Documentos de Rescisão 
 3: Boletos BMP 
 4: Boletos de Cobrança 
 5: Fichas de Registro 
 6: Folha de Pagamento, Férias e Rescisão 
 7: re FGTS 
 8: Listagem de Conferência 
 9: Recibos de Pagamento 
10: Recibos FOLK 
11: Relatório de Serviços Administrativos 
12: Resumo Geral Mês/Período 
13: NFs Fortaleza
14: Demonstrativo de Férias
15: NFs Eusébio
16: Cartas Singular
17: Rendimentos Protheus
18: Rendimentos Fortes
19: Planos de Saúde
20: Folha de Pagamento por Centro de Custo
'''
# Substitui o primeiro item da lista.
help_msg = '\n'.join(['\n 0: Retornar '] + main_msg.split('\n')[2:])
options: List[int] = list(range(len(main_msg.split('\n')) + 1))

def main():
    print('Manipulador de PDFs')
    print('V: ', VERSION)
    check_update()  # Verifica se há atualizações.
    main_hub()  # inicia o menu.


def check_update():
    last_version = get_last_version()
    if type(last_version) == str:
        if VERSION != get_last_version():
            print('Nova versão disponível!')
            print('Para baixar a nova versão, feche e exclua este arquivo (main.py) e execute o arquivo "download_last_version" dentro da pasta "configs".')
            input('Para continuar utilizando esta versão, pressione Enter')


def get_last_version():
    # Endpoint da API para buscar o histórico de commits de um arquivo específico
    url = f"https://api.github.com/repos/LuizGusQueiroz/Automacoes/commits"
    # Parâmetros da consulta, para buscar commits de um arquivo específico
    params = {'path': "KMF/Operacoes em PDF/_Manipulador de PDF/main.exe"}
    try:
        # Envia a requisição GET para a API do GitHub
        response = requests.get(url, params=params)
        response.raise_for_status()  # Levanta uma exceção se houver um erro na requisição
        # Extrai o JSON da resposta
        commits_data = response.json()
        if commits_data:
            # A mensagem do commit mais recente está no primeiro item da lista
            last_commit = commits_data[0]
            commit_message = last_commit['commit']['message']
            return commit_message
        else:
            return None
    except requests.exceptions.RequestException:
        return None
 


def process_option(option: int) -> None:
    """
    Processa a opção do usuário.
    """
    data = datetime.now().strftime("%d/%m/%Y")
    st = time.time()

    if option == 0:
        info_hub()
    elif option == 1:
        n_pags = documentos_admissao()
        tipo = 'Documentos de Admissão'
    elif option == 2:
        n_pags = documentos_rescisao()
        tipo = 'Documentos de Rescisão'
    elif option == 3:
        n_pags = boletos_bmp()
        tipo = 'Boletos BMP'
    elif option == 4:
        n_pags = boletos_cobranca()
        tipo = 'Boletos de Cobrança'
    elif option == 5:
        n_pags = fichas_de_registro()
        tipo = 'Fichas de Registro'
    elif option == 6:
        n_pags = folha_rescisao_ferias()
        tipo = 'Folha de Pagamento, Férias e Rescisão'
    elif option == 7:
        n_pags = guias_fgts()
        tipo = 'Guias FGTS'
    elif option == 8:
        n_pags = listagem_conferencia()
        tipo = 'Listagem de Conferência'
    elif option == 9:
        n_pags = recibos_pagamento()
        tipo = 'Recibos de Pagamento'
    elif option == 10:
        n_pags = recibos_folk()
        tipo = 'Recibos FOLK'
    elif option == 11:
        n_pags = rel_servicos_adm()
        tipo = 'Relatório de Serviços Administrativos'
    elif option == 12:
        n_pags = resumo_geral_mes_periodo()
        tipo = 'Resumo Geral Mês/Período'
    elif option == 13:
        n_pags = nfs_fortaleza()
        tipo = 'NFs Fortaleza'
    elif option == 14:
        n_pags = demonstrativo_ferias()
        tipo = 'Demonstrativo de Férias'
    elif option == 15:
        n_pags = nfs_eusebio()
        tipo = 'NFs Eusébio'
    elif option == 16:
        n_pags = cartas_singular()
        tipo = 'Cartas Singular'
    elif option == 17:
        n_pags = rendimentos_protheus()
        tipo = 'Rendimentos Protheus'
    elif option == 18:
        n_pags = rendimentos_fortes()
        tipo = 'Rendimentos Fortes'
    elif option == 19:
        n_pags = planos_de_saude()
        tipo = 'Planos de Saúde'
    elif option == 20:
        n_pags = folha_centro_custo()
        tipo = 'Folha por Centro de Custo'


    if option != 0:
        values = [[data, tipo, n_pags, time.time()-st]]
        salva_relatorio(values)


def main_hub():
    option: int = -1

    while option not in options:
        print('Digite uma opção de documento para separar.')
        print(main_msg)
        try:
            option = int(input('Escolha: '))
            limpa_terminal()
        except ValueError:
            pass
    process_option(option)


def info_hub() -> None:
    option: int = -1
    while option not in options:
        print('Escolha uma opção para abrir um arquivo do tipo e ler seu funcionamento.')
        print(help_msg)
        try:
            option = int(input('Escolha: '))
            limpa_terminal()
        except ValueError:
            pass
    if option not in options:
        info_hub()
    elif option != 0:
        help_doc(option)
        input('\nDigite enter para continuar')
        print('\n' * 50)
        main_hub()


def help_doc(option: int) -> None:
    os.startfile(os.getcwd() + fr'\configs\sample\{option}.pdf')
    with open('configs/READMEs.json', 'r', encoding='utf-8') as file:
        print(json.load(file)[str(option)])
    print('Um modelo deste arquivo está sendo aberto...')


def limpa_terminal() -> None:
    print('\n' * 35)


def salva_relatorio(row: List[List]):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    SAMPLE_SPREADSHEET_ID = "15gGHm67_W5maIas-4_YPSzE6R5f_CNJGcza_BJFlNBk"  # Código da planilha
    SAMPLE_RANGE_NAME = "Página1!A{}:D1000"  # Intervalo que será lido
    creds = None
    if os.path.exists("configs/token.json"):
        creds = Credentials.from_authorized_user_file("configs/token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "configs/client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("configs/token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME.format(2))
            .execute()
        )
        values = result.get("values", [])

        idx = 2 + len(values)

        result = (
            sheet.values()
            .update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME.format(idx),
                    valueInputOption='USER_ENTERED', body={"values": row})
            .execute()
        )

    except HttpError as err:
        print(err)



# ===================================================================
#                            Processamento de Arquivos
# ===================================================================


def documentos_admissao() -> int:  # 1
    # Cria a pasta de destino dos documentos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    tot_pags: int = 0
    # Itera por todos os arquivos .pdf.
    for file in [file for file in os.listdir() if '.pdf' in file.lower()]:
        # Cria a pasta para o arquivo.
        if not os.path.exists(f'Arquivos\\{file[:-4]}'):
            os.mkdir(f'Arquivos\\{file[:-4]}')
        with open(file, 'rb') as file_b:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF.
            pdf_reader = PdfReader(file_b)
            tot_pags += len(pdf_reader.pages)
            # Para cada página, identifica o tipo de documento e o nome do funcionário.
            for pag in tqdm(pdf_reader.pages):
                rows = pag.extract_text().split('\n')
                # Encontra o título do documento.
                idx = 0
                while not rows[idx].strip():
                    idx += 1
                titulo = rows[idx].strip()
                # Remove espaços do títulos
                titulo = ' '.join(titulo.split())
                # Acessa o nome com base no tipo de documento.
                if titulo == 'DECLARAÇÃO DE DEPENDENTES PARA FINS DE IMPOSTO DE RENDA':
                    nome = rows[2]
                elif titulo == 'TERMO LDPD':
                    row = rows[3]
                    nome = row[35:row.find(',', 35)].replace('_', '')
                elif titulo == 'R E C I B O D E E N T R E G A D A C A R T E I R A D E T R A B A L H O':
                    for row in rows:
                        if '(Carimbo e visto da empresa)' in row:
                            nome = row[28:-12]
                            break
                elif titulo == 'CTPS DIGITAL':
                    row = rows[3]
                    nome = row[row.find(' '):row.find(',', 4)]
                    # Remove espaços entre os nomes.
                    nome = ' '.join(nome.split())
                elif titulo == 'TERMO DE COMPROMISSO DE VALE-TRANSPORTE':
                    for i, row in enumerate(rows):
                        if 'SSPNome' in row:
                            nome = rows[i + 1]
                            break
                elif titulo == 'TERMO COLETIVO DE CESSÃO GRATUITA DE USO DE IMAGEM PARA DIVULGAÇÃO':
                    for row in rows:
                        if 'Empregado: ' in row:
                            nome = row[11:]
                            break
                elif titulo == 'REGISTRO DE EMPREGADONúmero:':
                    nome = rows[19][:-14]
                elif titulo == 'Termo de Responsabilidade':
                    nome = rows[6][:-10]
                elif titulo == 'Contrato de Experiência de Trabalho':
                    row = rows[2]
                    nome = row[row.rfind(',') + 1:row.find(' p', row.rfind(','))].strip()
                    # Remove espaços entre os nomes
                    nome = ' '.join(nome.split())
                elif titulo[:20] == 'A Controladora fica ':
                    nome = rows[30]
                elif titulo == 'AUTODECLARAÇÃO ÉTNICO-RACIAL':
                    nome = rows[13]
                # No Termo LGPD não tem o nome, fica na página seguinte, que começa com '" CLÁUSULA QUARTA:'
                # Então a página atual precisa ser guardada.
                elif titulo == 'TERMO LGPD':
                    row = rows[3]
                    nome = row[row.find(', eu') + 4:row.find(',', row.find(', eu') + 1)].strip()
                elif titulo == '" CLÁUSULA TERCEIRA: COMPARTILHAMENTO DE DADOS.':
                    nome = rows[31]
                elif titulo == '" CLÁUSULA QUARTA: RESPONSABILIDADE PELA SEGURANÇA DOS DADOS.':
                    nome = rows[29]
                elif titulo == '" CLÁUSULA QUINTA: TÉRMINO DO TRATAMENTO DOS DADOS.':
                    nome = rows[23]
                else:
                    print(f'Documento {[titulo]} não reconhecido!')
                    input()
                    continue

                file_name = f'Arquivos\\{file[:-4]}\\{nome}.pdf'
                pdf_writer = PdfWriter()
                # Verifica se já existe um arquivo para este funcionário
                if os.path.exists(file_name):
                    pdf_reader_temp = PdfReader(file_name)
                    # Copia todas as páginas do documento do funcionário para o writer
                    for page_num in range(len(pdf_reader_temp.pages)):
                        pdf_writer.add_page(pdf_reader_temp.pages[page_num])
                # Adiciona a página atual
                pdf_writer.add_page(pag)
                # Salva o arquivo
                with open(file_name, "wb") as output_pdf:
                    pdf_writer.write(output_pdf)
    return tot_pags


def documentos_rescisao() -> int:  # 2

    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    tot_pags: int = 0
    for arq in [file for file in os.listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf = PdfReader(file)
            tot_pags += len(pdf.pages)
            for pag in tqdm(pdf.pages):
                rows = pag.extract_text().split('\n')
                tipo = rows[0]
                if tipo == 'TERMO DE RESCISÃO DO CONTRATO DE TRABALHO':
                    cpf = rows[40]
                    nome = rows[31]
                elif tipo == 'TERMO DE QUITAÇÃO DE RESCISÃO DO CONTRATO DE TRABALHO':
                    cpf = rows[10][:14]
                    nome = rows[8]
                else:
                    print(f'Tipo de documento não suportado: [{tipo}].')
                    continue

                cpf = ''.join(char for char in cpf if char.isnumeric())
                file_name = f'Arquivos/{nome}{cpf}.pdf'
                writer = PdfWriter()
                if os.path.exists(file_name):
                    pdf_temp = PdfReader(file_name)
                    # Copia todas as páginas do documento do funcionário para o writer
                    for page_num in range(len(pdf_temp.pages)):
                        writer.add_page(pdf_temp.pages[page_num])
                # Adiciona a página atual.
                writer.add_page(pag)
                # Salva o arquivo
                with open(file_name, "wb") as output_pdf:
                    writer.write(output_pdf)
    return tot_pags


def boletos_bmp() -> int:  # 3
    # Cria a pasta de destino dos documentos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    tot_pags: int = 0
    # Itera por todos os arquivos .pdf.
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for file in tqdm(files):
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b).pages[0]
            rows = pdf.extract_text().split('\n')
            row = rows[-2]
            nome = row[:row.find(' - CPF/CNPJ: ')]
            tot_pags += len(PdfReader(file_b).pages)
        os.rename(file, f'Arquivos/BOLETO - {nome}.pdf')
    return tot_pags


def boletos_cobranca() -> int:  # 4
    # Cria a pasta de destino dos recibos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    tot_pags: int = 0
    # Itera por todos os arquivos .pdf.
    for arq in [file for file in os.listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            tot_pags += len(pdf_reader.pages)
            # Itera sobre todas as páginas do PDF
            for page_pdf in tqdm(pdf_reader.pages):
                page = page_pdf.extract_text().split('\n')
                for i, row in enumerate(page):
                    if 'UF:CEP:Data Vencimento: ' in row:
                        condominio = row[row.rfind(':') + 2:]
                        cnpj = ''.join(char for char in page[i + 1] if char.isnumeric())
                        break
                nome_arq = f'Arquivos/{condominio}-{cnpj}.pdf'
                writer = PdfWriter()
                writer.add_page(page_pdf)
                with open(nome_arq, 'wb') as output:
                    writer.write(output)
    return tot_pags


def fichas_de_registro() -> int:  # 5
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    tot_pags: int = 0

    for file in [file for file in os.listdir() if '.pdf' in file]:
        diretorio = f'Arquivos/{file[:-4]}'
        if not os.path.exists(diretorio):
            os.mkdir(diretorio)
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b)
            tot_pags += len(pdf.pages)
            # Percorre todas as páginas do PDF.
            for page in tqdm(pdf.pages):
                rows = page.extract_text().split('\n')
                for row in rows:
                    if 'Dados Pessoais' in row:
                        nome = row[:-14]
                        break
                writer = PdfWriter()
                writer.add_page(page)
                # Salva a página em um novo arquivo PDF
                with open(f'{diretorio}/{nome}.pdf', 'wb') as output_file:
                    writer.write(output_file)
    return tot_pags


def folha_rescisao_ferias() -> int:  # 6
    # Cria a pasta de destino dos recibos
    if not os.path.exists('Folhas de Pagamento'):
        os.mkdir('Folhas de Pagamento')
    tot_pags: int = 0

    for arq in [file for file in os.listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            pdf_writer = PdfWriter()
            lotacao = ''
            tot_pags += len(pdf_reader.pages)
            for page_pdf in tqdm(pdf_reader.pages):
                page = page_pdf.extract_text().split('\n')
                tipo = ' '.join(page[0].split()[:3])
                # Verifica o tipo de arquivo
                if tipo == 'Folha de Pagamento':
                    lotacao_nova = page[6]
                elif tipo == 'Listagem de Férias':
                    lotacao_nova = page[5]
                elif tipo == 'Listagem de Rescisão':
                    lotacao_nova = page[5]
                else:
                    print(tipo)
                    continue
                # Verifica se já há umas pasta para o tipo
                if not os.path.exists(f'Folhas de Pagamento/{tipo}'):
                    os.mkdir(f'Folhas de Pagamento/{tipo}')
                # Verifica se está na página de resumo ou se a lotacao for a mesma, se sim,
                # junta as páginas, caso contrário, salva o arquivo atual e cria um pdf novo.
                if 'Total Geral ' in lotacao_nova or lotacao_nova != lotacao:
                    if pdf_writer.pages:
                        with open(f'Folhas de Pagamento/{tipo}/{lotacao.replace('/', '')}.pdf', 'wb') as output_file:
                            pdf_writer.write(output_file)
                        pdf_writer = PdfWriter()
                    lotacao = lotacao_nova
                    pdf_writer.add_page(page_pdf)
                else:
                    pdf_writer.add_page(page_pdf)
    return tot_pags


def guias_fgts() -> int:  # 7
    def get_de_para() -> pd.DataFrame|None:
        files = [file for file in os.listdir() if '.xls' in file]
        if len(files) == 0:
            return None
        df = pd.read_excel(files[0])
        df.columns = df.iloc[0]
        return df


    clientes: pd.DataFrame|None = get_de_para()
    tem_excel: bool = clientes is not None
    # Cria a pasta de destino dos recibos
    if not os.path.exists('Arquivos do fgts'):
        os.mkdir('Arquivos do fgts')
    tot_pags: int = 0

    for arq in [file for file in os.listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            tot_pags += len(pdf_reader.pages)
            # Itera sobre todas as páginas do PDF
            for page_pdf in tqdm(pdf_reader.pages):
                page = page_pdf.extract_text().split('\n')

                if tem_excel:
                    if 'Tomador: ' in page[10]:
                        cnpj = page[10][page[10].find('Tomador: '):][9:]
                        if cnpj == 'Sem Tomador':
                            continue

                            nome = clientes['Nome'][clientes['Inscrição']==cnpj].values
                            if len(nome) == 1:
                                nome = nome[0].replace('/', '') + '.pdf'
                            else:
                                nome = '_NaoEncontrados.pdf'

                        pdf_writer = PdfWriter()
                        # Adiciona a página atual ao objeto PdfWriter
                        pdf_writer.add_page(page_pdf)

                        # Verifica se o arquivo com este nome já existe, caso exista, junta-o com o novo arquivo
                        if nome in os.listdir('Arquivos do fgts'):
                            old_pdf = PdfReader(f'Arquivos do fgts/{nome}')
                            for page in old_pdf.pages:
                                pdf_writer.add_page(page)

                        # Salva a página em um novo arquivo PDF
                        with open(f'Arquivos do fgts/{nome}', 'wb') as output_file:
                            pdf_writer.write(output_file)
                else:
                    for row in page:
                        if 'Tomador: ' in row:
                            cnpj = row[row.find('Tomador: ')+9:]
                            nome = f'{cnpj.replace('/', '').replace('-', '').replace('.', '')}.pdf'
                            break
                    pdf_writer = PdfWriter()
                    # Adiciona a página atual ao objeto PdfWriter
                    pdf_writer.add_page(page_pdf)

                    # Verifica se o arquivo com este nome já existe, caso exista, junta-o com o novo arquivo
                    if nome in os.listdir('Arquivos do fgts'):
                        old_pdf = PdfReader(f'Arquivos do fgts/{nome}')
                        for page in old_pdf.pages:
                            pdf_writer.add_page(page)

                    # Salva a página em um novo arquivo PDF
                    with open(f'Arquivos do fgts/{nome}', 'wb') as output_file:
                        pdf_writer.write(output_file)
    return tot_pags


def listagem_conferencia() -> int:  # 8
    """
    Lista todos os arquivos PDF no diretório atual (só irá funcionar para Listagens de Conferência)
    e separa em subarquivos, agrupados pela lotação.
    """
    # Cria a pasta de destino dos recibos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    tot_pags: int = 0

    for arq in [file for file in os.listdir() if '.pdf' in file]:
        folder_name = arq.replace('.pdf', '').replace('/', '')
        if not os.path.exists(f'Arquivos/{folder_name}'):
            os.mkdir(f'Arquivos/{folder_name}')

        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            pdf_writer = PdfWriter()
            lotacao = ''
            tot_pags += len(pdf_reader.pages)
            for page_pdf in tqdm(pdf_reader.pages):
                page = page_pdf.extract_text().split('\n')
                # Acessa a lotação
                lotacao_nova = page[6]
                # Verifica se a lotação é a mesma, se for, junta as páginas,
                # caso contrário, salva o arquivo atual e cria um pdf novo.
                if lotacao_nova != lotacao:
                    if pdf_writer.pages:
                        with open(f'Arquivos/{folder_name}/{lotacao}.pdf', 'wb') as output_file:
                            pdf_writer.write(output_file)
                        pdf_writer = PdfWriter()
                    lotacao = lotacao_nova
                    pdf_writer.add_page(page_pdf)
                else:
                    pdf_writer.add_page(page_pdf)
            # Não é necessário salvar o último arquivo em memória, pois é apenas o resumo.
    return tot_pags


def recibos_pagamento() -> int:  # 9
    # Cria a pasta de destino dos recibos
    if not os.path.exists('Recibos de Pagamento'):
        os.mkdir('Recibos de Pagamento')
    tot_pags: int = 0

    escolha = ''
    while escolha not in ['1', '2']:
        escolha = input('-' * 30 + '\n'
                        '1: Separar por funcionário.\n'
                        '2: Separar por Lotação.\n'
                        'Escolha: ')

    files = [file for file in os.listdir() if '.pdf' in file]

    for arq in files:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            tot_pags += len(pdf_reader.pages)
            if escolha == '1':  # Separa por funcionário
                # Itera sobre todas as páginas do PDF
                for pag in tqdm(pdf_reader.pages):
                    rows = pag.extract_text().split('\n')
                    # Acessa a linha que contém o nome do empregado.
                    nome = rows[11]
                    # Acessa a linha que contém a lotação do empregado.
                    lotacao = rows[9][:-5]
                    file_name = f'Recibos de Pagamento\\{lotacao}-{nome}.pdf'.replace('/', '')
                    pdf_writer = PdfWriter()
                    # Adiciona a página atual ao objeto PdfWriter
                    pdf_writer.add_page(pag)

                    # Salva a página em um novo arquivo PDF
                    with open(file_name, 'wb') as output_file:
                        pdf_writer.write(output_file)

            elif escolha == '2':  # Separa por lotação
                for pag in tqdm(pdf_reader.pages):
                    rows = pag.extract_text().split('\n')
                    lotacao = rows[9][:-5]

                    file_name = f'Recibos de Pagamento\\{lotacao}.pdf'.replace('/', '')
                    pdf_writer = PdfWriter()
                    # Verifica se já existe um arquivo para esta lotação.
                    if os.path.exists(file_name):
                        pdf_reader_temp = PdfReader(file_name)
                        # Copia todas as páginas do documento da lotação para o writer.
                        for page_num in range(len(pdf_reader_temp.pages)):
                            pdf_writer.add_page(pdf_reader_temp.pages[page_num])
                    # Adiciona a página atual
                    pdf_writer.add_page(pag)
                    # Salva o arquivo
                    with open(file_name, "wb") as output_pdf:
                        pdf_writer.write(output_pdf)
    return tot_pags


def recibos_folk() -> int:  # 10
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    tot_pags: int = 0

    files = [file for file in os.listdir() if '.pdf' in file.lower()]

    for file in files:
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file)
        tot_pags += len(pdf.pages)
        for page in tqdm(pdf.pages):
            rows = page.extract_text().split('\n')
            nome = rows[1][rows[1].find('.')+1:]
            writer = PdfWriter()
            writer.add_page(page)
            with open(f'Arquivos/RECIBO - {nome}.pdf', 'wb') as output:
                writer.write(output)
    return tot_pags


def rel_servicos_adm() -> int:  # 11
    # Cria a pasta de destino dos arquivos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    tot_pags: int = 0
    for arq in [file for file in os.listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            tot_pags += len(pdf_reader.pages)
            # Itera sobre todas as páginas do PDF
            for page in tqdm(pdf_reader.pages):
                rows = page.extract_text().split('\n')

                lotacao = rows[0].replace('.', '').replace('/', '').replace('\\', '')[:-37]

                pdf_writer = PdfWriter()
                # Adiciona a página atual ao objeto PdfWriter
                pdf_writer.add_page(page)
                # Salva a página em um novo arquivo PDF
                with open(f'Arquivos/{lotacao}.pdf', 'wb') as output_file:
                    pdf_writer.write(output_file)
    return tot_pags


def resumo_geral_mes_periodo() -> int:  # 12
    # Cria a pasta de destino dos recibos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    tot_pags: int = 0
    for arq in [file for file in os.listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            pdf_writer = PdfWriter()
            empresa = ''
            tot_pags += len(pdf_reader.pages)
            for page_pdf in tqdm(pdf_reader.pages):
                page = page_pdf.extract_text().split('\n')
                # Acessa o nome e CNPJ da empresa
                for row in page:
                    if 'Empresa: ' in row:
                        idx = 1
                        while not row[-idx].isnumeric():
                            idx += 1
                        row = row[8:1 - idx].split()
                        cnpj = ''.join(i for i in row[-1] if i.isnumeric())
                        idx = 0
                        while row[idx] != '-':
                            idx += 1
                        empresa_nova = ' '.join(row[:idx])
                        break

                # Verifica se a empresa e a mesma, se for, junta as páginas,
                # caso contrário, salva o arquivo atual e cria um pdf novo.
                if empresa_nova != empresa:
                    if pdf_writer.pages:
                        with open(f'Arquivos/{empresa}-{cnpj}.pdf', 'wb') as output_file:
                            pdf_writer.write(output_file)
                        pdf_writer = PdfWriter()
                    empresa = empresa_nova
                    pdf_writer.add_page(page_pdf)
                else:
                    pdf_writer.add_page(page_pdf)
            # Salva o último arquivo aberto
            with open(f'Arquivos/{empresa}-{cnpj}.pdf', 'wb') as output_file:
                pdf_writer.write(output_file)
            pdf_writer = PdfWriter()
    return tot_pags


def nfs_fortaleza() -> int:  # 32
    tot_pags: int = 0

    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for file in files:
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b).pages[0]
            rows = pdf.extract_text().split('\n')
            tot_pags += len(PdfReader(file_b).pages)
        if rows[0] == 'Número da':
            # Modelo 1
            cnpj = ' ERRO '
            num_nf = ''.join(i for i in rows[1].split()[0] if i.isnumeric())
            for row in rows:
                if 'Complemento:' in row:
                    nome = row[12:].strip()
                    break
        elif rows[0] == 'Dados do Prestador de Serviços':
            # modelo 2
            primeiro = True
            for i, row in enumerate(rows):
                if row == 'NFS-e':
                    num_nf = rows[i + 1]
                if row == 'Razão Social/Nome':
                    if primeiro:
                        primeiro = False
                    else:
                        nome = rows[i + 1]
                        cnpj = ''.join([char for char in rows[i + 3] if char.isnumeric()])
                        break
        else:
            continue
        os.rename(file, f'NF {nome}-{cnpj}.pdf')
    return tot_pags


def demonstrativo_ferias() -> int:
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    n_pags = 0
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for file in files:
        with open(file, 'rb') as file:
            pdf_reader = PdfReader(file)
            n_pags = len(pdf_reader.pages)
            for page in tqdm(pdf_reader.pages):
                rows = page.extract_text().split()
                start = 4
                for i, row in enumerate(rows):
                    if row in ['LTDA', 'S/A', 'BEM-TE-VI', 'CONDOMINIOS', 'Ltda', 'REMOTA',
                               'EIRELI', 'ME', 'PINHO', 'EMPRESARIAL', 'S.A.']:
                        start = i + 1
                        break
                for i, row in enumerate(rows):
                    if 'DEMONSTRATIVO' in row:
                        nome = ' '.join(rows[start:i]+[row[:-13]])
                        break
                pdf_writer = PdfWriter()
                pdf_writer.add_page(page)
                with open(f'Arquivos/{nome}.pdf', 'wb') as output:
                    pdf_writer.write(output)
    return n_pags

def nfs_eusebio() -> int:
    n_pags = 0
    files = [file for file in os.listdir() if '.pdf' in file.lower()]

    for file in tqdm(files):
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b)
            n_pags += len(pdf.pages)
            rows = pdf.pages[0].extract_text().split('\n')
            nome = rows[-3].split('Endereço')[-1]
            cnpj = ''.join([char for char in rows[-1].split()[0] if char.isnumeric()])
            nome_arq = f'{nome}-{cnpj}.pdf'
        os.rename(file, nome_arq)
    return n_pags


def cartas_singular():
    n_pags = 0
    if not os.path.exists('Cartas'):
        os.mkdir('Cartas')
    files = [file for file in os.listdir() if '.pdf' in file.lower()]

    for file in files:
        writer = PdfWriter()
        primeiro = True
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b)
            n_pags += len(pdf.pages)
            for page in tqdm(pdf.pages):
                rows = page.extract_text().split('\n')
                nome = rows[1].replace('/', '')
                if rows[0] == 'Prezados, ' and not primeiro:
                    with open(f'Cartas/{nome}.pdf', 'wb') as output:
                        writer.write(output)
                    writer = PdfWriter()
                writer.add_page(page)
                primeiro = False
    return n_pags


def rendimentos_protheus() -> int:
    tot_pags = 0
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    writer = PdfWriter()
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    for file in files:
        with (open(file, 'rb') as file_b):
            pdf = PdfReader(file_b)
            tot_pags += len(pdf.pages)
            for page in tqdm(pdf.pages):
                rows = page.extract_text().split('\n')
                if len(rows) == 1:
                    continue
                if not len(writer.pages):
                    for i, row in enumerate(rows):
                        if ' CPF' in row:
                            row = row.split()
                            cpf = row[2]
                            nome = ' '.join(row[5:-1])
                            for char in ['|', '/', '\\']:
                                nome = nome.replace(char, '')
                            break
                writer.add_page(page)
                if len(writer.pages) == 2:
                    file_name = f'Arquivos/{nome}-{cpf}.pdf'
                    with open(file_name, 'wb') as output:
                        writer.write(output)        
                    writer = PdfWriter()
    return tot_pags


def rendimentos_fortes() -> int:
    tot_pags = 0
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    writer = PdfWriter()
    cpf = ''
    nome = ''
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for file in files:
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b)
            tot_pags += len(pdf.pages)
            for page in tqdm(pdf.pages):
                rows = page.extract_text().split('\n')
                if rows[0] == 'MINISTÉRIO DA FAZENDA':
                    # MINISTÉRIO DA FAZENDA indica o começo de um novo funcionário, então o
                    # conteúdo atual é salvo, se existir.
                    if len(writer.pages):
                        file_name = f'Arquivos/{nome}-{cpf}-{cnpj}.pdf'
                        with open(file_name, 'wb') as output:
                            writer.write(output)
                        # Inicia um novo writer
                        writer = PdfWriter()
                    writer.add_page(page)
                    # Guarda o CNPJ da empresa.
                    cnpj = ''.join(char for char in rows[7] if char.isnumeric())
                    # Procura o nome e CPF no novo documento.
                    for i, row in enumerate(rows):
                        achou = False
                        if 'Título de Eleitor' in row:
                            achou = True
                            cpf = ''.join(char for char in row if char.isnumeric())
                            nome = rows[i+2]
                            for char in ['|', '/', '\\']:
                                nome = nome.replace(char, '')
                            break
                    if not achou:
                        raise Exception(f'Nome e CPF não encontrados: {file}')
                else:
                    writer.add_page(page)
            # Salva o último aberto
            file_name = f'Arquivos/{nome}-{cpf}.pdf'
            with open(file_name, 'wb') as output:
                writer.write(output)

    return tot_pags


def planos_de_saude() -> int:
    def eh_dependente(row: str) -> bool:
        return ',' not in row.split()[0]
    tot_pags = 0
    df = pd.DataFrame(columns=['Empresa', 'Lotação', 'Operador', 'Plano', 'Nome',
                               'Dependente', 'Valor Funcionário', 'Valor Empresa'])
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for file in files:
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b)
            tot_pags += len(pdf.pages)
            for page in tqdm(pdf.pages):
                rows = page.extract_text().split('\n')
                empresa = ' '.join(rows[1].split()[1:])
                operador = rows[3][10:]
                lotacao = rows[6]

                for i, row in enumerate(rows[7:-1], start=7):
                    if '-' in row:
                        if ' Total: ' in row:
                            continue
                        row = row.split()
                        plano = ' '.join(row[3:-2])
                        ii = i - 1
                        # Busca a linha com o nome do funcionário.
                        while ('-' in rows[ii]) or eh_dependente(rows[ii]):
                            ii -= 1

                        nome = ' '.join(rows[ii].split()[3:-2])
                        valor_fun = row[0]
                        valor_emp = row[1]
                        df.loc[len(df)] = [empresa, lotacao, operador, plano, nome, '', valor_fun, valor_emp]
                        ii = i + 1
                        while eh_dependente(rows[ii]):
                            row = rows[ii].split()
                            nome_dep = ' '.join(row[1:-5])
                            valor_fun = row[-5]
                            valor_emp = row[-4]
                            df.loc[len(df)] = [empresa, lotacao, operador, plano, nome, nome_dep, valor_fun, valor_emp]
                            ii += 1
            # Cálculo dos totais.
            df['é dependente'] = df['Dependente'].apply(lambda x: ['Não', 'Sim'][bool(x)])
            df['Valor Funcionário'] = df['Valor Funcionário'].apply(lambda x: float(x.replace(',', '.')))
            df['Valor Empresa'] = df['Valor Empresa'].apply(lambda x: float(x.replace(',', '.')))
            df_totais = df.groupby(['Empresa', 'Plano', 'é dependente'])[['Valor Funcionário', 'Valor Empresa']].sum().reset_index()
            df_totais['Total Funcionários'] = df.groupby(['Empresa', 'Plano', 'é dependente'])['Nome'].nunique().values
            df_totais['Total Dependentes'] = df.groupby(['Empresa', 'Plano', 'é dependente'])['Dependente'].nunique().values
            for row in range(len(df_totais)):
                if df_totais['é dependente'].iloc[row] == 'Não':
                    df_totais.at[row, 'Total Dependentes'] = 0
                else:
                    df_totais.at[row, 'Total Funcionários'] = 0
            # Calcula a soma dos totais.
            df_totais.loc[len(df_totais)] = ['TOTAIS', '', '',
                                             df_totais['Valor Funcionário'].sum(), df_totais['Valor Empresa'].sum(),
                                             df_totais['Total Funcionários'].sum(), df_totais['Total Dependentes'].sum()]
            df.to_excel('planos.xlsx', index=False)
            df_totais.to_excel('totais.xlsx', index=False)
    return tot_pags


def folha_centro_custo() -> int:
    n_pags = 0
    centro_custo = ''
    codigo = ''
    novo_centro_custo = '-'
    novo_codigo = '-'
    writer = PdfWriter()
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')

    for file in [file for file in os.listdir() if '.pdf' in file.lower()]:
        with open(file, 'rb') as file:
            pdf = PdfReader(file)
            n_pags += len(pdf.pages)
            for page in tqdm(pdf.pages):
                rows = page.extract_text().split('\n')
                for row in rows:
                    if 'C Custo' in row:
                        novo_centro_custo = row.split(': ')[-1].replace('/', '')
                        novo_codigo = row.split(': ')[2][:-9]
                        break
                if novo_centro_custo != centro_custo:
                    if len(writer.pages) > 0:
                        # Salva o atual
                        with open(f'Arquivos/{codigo}-{centro_custo}.pdf', 'wb') as output:
                            writer.write(output)
                    centro_custo = novo_centro_custo
                    codigo = novo_codigo
                    writer = PdfWriter()
                    writer.add_page(page)
                else:
                    writer.add_page(page)
            # Salva o atual
            with open(f'Arquivos/{codigo}-{centro_custo}.pdf', 'wb') as output:
                writer.write(output)
    return n_pags




if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        input()
