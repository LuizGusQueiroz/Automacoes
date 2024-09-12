from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
from typing import List
import pandas as pd
from sys import exit
import json
import os


VERSION: str = '0.03.01'

main_msg: str = '''
 0: Informações 
 1: Documentos de Admissão 
 2: Documentos de Rescisão 
 3: Boletos BMP 
 4: Boletos de Cobrança 
 5: Fichas de Registro 
 6: Folha de Pagamento, Férias e Rescisão 
 7: Guias FGTS 
 8: Listagem de Conferência 
 9: Recibos de Pagamento 
10: Recibos FOLK 
11: Relatório de Serviços Administrativos 
12: Resumo Geral Mês/Período 
'''
# Substitui o primeiro item da lista.
help_msg = '\n'.join(['\n 0: Retornar '] + main_msg.split('\n')[2:])
options: List[int] = list(range(len(main_msg.split('\n')) + 1))


def main():
    print('Manipulador de PDFs')
    print('V: ', VERSION)
    main_hub()  # inicia o menu.


def process_option(option: int) -> None:
    """
    Processa a opção do usuário.
    """
    if option == 0:
        info_hub()
    elif option == 1:
        documentos_admissao()
    elif option == 2:
        documentos_rescisao()
    elif option == 3:
        boletos_bmp()
    elif option == 4:
        boletos_cobranca()
    elif option == 5:
        fichas_de_registro()
    elif option == 6:
        folha_rescisao_ferias()
    elif option == 7:
        guias_fgts()
    elif option == 8:
        listagem_conferencia()
    elif option == 9:
        recibos_pagamento()
    elif option == 10:
        recibos_folk()
    elif option == 11:
        rel_servicos_adm()
    elif option == 12:
        resumo_geral_mes_periodo()


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
    else:
        main_hub()


def help_doc(option: int) -> None:
    os.startfile(os.getcwd() + fr'\configs\sample\{option}.pdf')
    with open('configs/READMEs.json', 'r', encoding='utf-8') as file:
        print(json.load(file)[str(option)])
    print('Um modelo deste arquivo está sendo aberto...')


def limpa_terminal() -> None:
    print('\n' * 30)


def documentos_admissao():
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


def documentos_rescisao():

    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')

    for arq in [file for file in os.listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf = PdfReader(file)

            for pag in pdf.pages:#tqdm(pdf.pages):
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


def resumo_geral_mes_periodo():
    # Cria a pasta de destino dos recibos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')

    for arq in [file for file in os.listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            pdf_writer = PdfWriter()
            empresa = ''

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


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        input()
