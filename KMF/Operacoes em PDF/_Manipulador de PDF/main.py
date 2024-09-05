from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
from typing import List
import pandas as pd
from sys import exit
import os

VERSION = '0.01.01'


def main():
    print('Manipulador de PDFs \nV:', VERSION)
    option: int = main_hub()
    if option == 0:
        info_hub()
    elif option == 1:
        admissoes()
    elif option == 2:
        boletos_bmp()
    elif option == 3:
        boletos_cobranca()
    elif option == 4:
        fichas_de_registro()
    elif option == 5:
        folha_rescisao_ferias()
    elif option == 6:
        guias_fgts()
    elif option == 7:
        listagem_conferencia()
    elif option == 8:
        recibos_pagamento()
    elif option == 9:
        recibos_folk()
    elif option == 10:
        rel_servicos_adm()


def main_hub() -> int:
    n_options: int = 15
    options: List[int] = list(range(n_options + 1))
    option: int = -1
    msg: str = '''
     0: Informações \n
     1: Documentos Admissionais \n
     2: Boletos BMP \n
     3: Boletos de Cobrança \n
     4: Fichas de Registro \n
     5: Folha de Pagamento, Férias e Rescisão \n
     6: Guias FGTS \n
     7: Listagem de Conferência \n
     8: Recibos de Pagamento \n
     9: Recibos FOLK \n
    10: Relatório de Serviços Administrativos \n
    '''

    while option not in options:
        print(msg)
        try:
            option = int(input())
        except ValueError:
            pass
    return option


def info_hub():
    ...


def admissoes():
    # Cria a pasta de destino dos documentos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    # Itera por todos os arquivos .pdf.
    for file in [file for file in os.listdir() if '.pdf' in file.lower()]:
        # Cria a pasta para o arquivo.
        if not os.path.exists(f'Documentos\\{file[:-4]}'):
            os.mkdir(f'Documentos\\{file[:-4]}')
        with open(file, 'rb') as file_b:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF.
            pdf_reader = PdfReader(file_b)
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

                file_name = f'Documentos\\{file[:-4]}\\{nome}.pdf'
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


def boletos_bmp():
    # Cria a pasta de destino dos documentos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    # Itera por todos os arquivos .pdf.
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for file in tqdm(files):
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b).pages[0]
            rows = pdf.extract_text().split('\n')
            row = rows[-2]
            nome = row[:row.find(' - CPF/CNPJ: ')]
        os.rename(file, f'Arquivos/BOLETO - {nome}.pdf')


def boletos_cobranca():
    # Cria a pasta de destino dos recibos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    # Itera por todos os arquivos .pdf.
    for arq in [file for file in os.listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            # Itera sobre todas as páginas do PDF
            for page_pdf in tqdm(pdf_reader.pages):
                page = page_pdf.extract_text().split('\n')
                for row in page:
                    if 'UF:CEP:Data Vencimento: ' in row:
                        condominio = row[row.rfind(':') + 2:]
                        break
                for row in page:
                    if 'Boleto referente:' in row:
                        numero = row[row.find(':') + 1:row.find('/', row.find(' '))]
                        if len(numero) > 20:
                            numero = row[row.rfind(' ') + 1:row.rfind('/')]
                        break
                nome_arq = f'{condominio}-{numero}.pdf'
                pdf_writer = PdfWriter()
                # Adiciona a página atual ao objeto PdfWriter
                pdf_writer.add_page(page_pdf)
                # Salva a página em um novo arquivo PDF.
                with open(f'Arquivos\\{nome_arq}', 'wb') as output_file:
                    pdf_writer.write(output_file)


def fichas_de_registro():
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    for file in [file for file in os.listdir() if '.pdf' in file]:
        diretorio = f'Arquivos/{file[:-4]}'
        if not os.path.exists(diretorio):
            os.mkdir(diretorio)
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b)
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


def folha_rescisao_ferias():
    # Cria a pasta de destino dos recibos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')

    for arq in [file for file in os.listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            pdf_writer = PdfWriter()
            lotacao = ''

            for page_pdf in tqdm(pdf_reader.pages):
                page = page_pdf.extract_text().split('\n')
                tipo = ' '.join(page[0].split()[:3])
                # Verifica o tipo de arquivo
                if tipo == 'Folha de Pagamento':
                    lotacao_nova = page[5]
                elif tipo == 'Listagem de Férias':
                    lotacao_nova = page[4]
                elif tipo == 'Listagem de Rescisão':
                    lotacao_nova = page[4]
                else:
                    print(tipo)
                    continue
                # Verifica se já há umas pasta para o tipo
                if not os.path.exists(f'Arquivos/{tipo}'):
                    os.mkdir(f'Arquivos/{tipo}')
                # Verifica se está na página de resumo ou se a lotacao for a mesma, se sim,
                # junta as páginas, caso contrário, salva o arquivo atual e cria um pdf novo.
                if 'Total Geral ' in lotacao_nova or lotacao_nova != lotacao:
                    if pdf_writer.pages:
                        with open(f'Arquivos/{tipo}/{lotacao.replace('/', '')}.pdf', 'wb') as output_file:
                            pdf_writer.write(output_file)
                        pdf_writer = PdfWriter()
                    lotacao = lotacao_nova
                    pdf_writer.add_page(page_pdf)
                else:
                    pdf_writer.add_page(page_pdf)


def guias_fgts():
    def get_de_para() -> pd.DataFrame:
        files = [file for file in os.listdir() if '.xls' in file]
        if len(files) != 1:
            print('Tabela de clientes não encontrada.')
            input()
            exit()
        df = pd.read_excel(files[0])
        df.columns = df.iloc[0]
        return df

    clientes: pd.DataFrame = get_de_para()
    # Cria a pasta de destino dos recibos
    if not os.path.exists('Guias'):
        os.mkdir('Guias')

    for arq in [file for file in os.listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)

            # Itera sobre todas as páginas do PDF
            for page_pdf in tqdm(pdf_reader.pages):
                page = page_pdf.extract_text().split('\n')

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
                    if nome in os.listdir('Guias'):
                        old_pdf = PdfReader(f'Guias/{nome}')
                        for page in old_pdf.pages:
                            pdf_writer.add_page(page)

                    # Salva a página em um novo arquivo PDF
                    with open(f'Guias/{nome}', 'wb') as output_file:
                        pdf_writer.write(output_file)


def listagem_conferencia() -> None:
    """
    Lista todos os arquivos PDF no diretório atual (só irá funcionar para Listagens de Conferência)
    e separa em subarquivos, agrupados pela lotação.
    """
    # Cria a pasta de destino dos recibos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')

    for arq in [file for file in os.listdir() if '.pdf' in file]:
        folder_name = arq.replace('.pdf', '').replace('/', '')
        if not os.path.exists(f'Arquivos/{folder_name}'):
            os.mkdir(f'Arquivos/{folder_name}')

        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            pdf_writer = PdfWriter()
            lotacao = ''

            for page_pdf in tqdm(pdf_reader.pages):
                page = page_pdf.extract_text().split('\n')
                # Acessa a lotação
                lotacao_nova = page[5]
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


def recibos_pagamento():
    # Cria a pasta de destino dos recibos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')

    escolha = ''
    while escolha not in ['1', '2']:
        escolha = input('---------------\n'
                        '1: Separar por funcionário.\n'
                        '2: Separar por Lotação.\n'
                        'Escolha: ')

    files = [file for file in os.listdir() if '.pdf' in file]

    for arq in files:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)

            if escolha == '1':  # Separa por funcionário
                # Itera sobre todas as páginas do PDF
                for pag in tqdm(pdf_reader.pages):
                    rows = pag.extract_text().split('\n')
                    # Acessa a linha que contém o nome do empregado.
                    nome = rows[11]
                    # Acessa a linha que contém a lotação do empregado.
                    lotacao = rows[9][:-5]
                    file_name = f'Recibos\\{lotacao}-{nome}.pdf'.replace('/', '')
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

                    file_name = f'Arquivos\\{lotacao}.pdf'.replace('/', '')
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


def recibos_folk():
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')

    files = [file for file in os.listdir() if '.pdf' in file.lower()]

    for file in files:
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file)
        for page in tqdm(pdf.pages):
            rows = page.extract_text().split('\n')
            nome = rows[1][rows[1].find('.')+1:]
            writer = PdfWriter()
            writer.add_page(page)
            with open(f'Arquivos/RECIBO - {nome}.pdf', 'wb') as output:
                writer.write(output)


def rel_servicos_adm():
    # Cria a pasta de destino dos arquivos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')

    for arq in [file for file in os.listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)

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



if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        input()
