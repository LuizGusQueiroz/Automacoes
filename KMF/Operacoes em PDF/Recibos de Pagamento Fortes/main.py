import os
from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm


def recibos_pagamentos_fortes() -> int:
    tot_pags = 0
    # Cria a pasta de destino dos recibos
    if not os.path.exists('Recibos'):
        os.mkdir('Recibos')

    escolha = ''
    while escolha not in ['1', '2']:
        print('-'*50)
        escolha = input('1: Separar por funcionário.\n'
                        '2: Separar por Lotação.\n'
                        'Escolha: ')

    files = [file for file in os.listdir() if '.pdf' in file]

    for arq in files:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf = PdfReader(file)
            tot_pags += len(pdf.pages)
            for pag in tqdm(pdf.pages):
                writer = PdfWriter()
                rows = pag.extract_text().split('\n')
                lotacao = rows[9][:-5]
                cnpj = ''.join(char for char in rows[5].split()[1] if char.isnumeric())
                if escolha == '1':
                    # Acessa a linha que contém o nome do empregado.
                    nome = rows[11]
                    file_name = f'Recibos\\{lotacao}-{nome}-{cnpj}.pdf'.replace('/', '')
                else:
                    file_name = f'Recibos\\{lotacao}-{cnpj}.pdf'.replace('/', '')
                    # Verifica se já existe um arquivo para esta lotação.
                    if os.path.exists(file_name):
                        pdf_reader_temp = PdfReader(file_name)
                        # Copia todas as páginas do documento da lotação para o writer.
                        for page_num in range(len(pdf_reader_temp.pages)):
                            writer.add_page(pdf_reader_temp.pages[page_num])
                # Adiciona a página atual
                writer.add_page(pag)
                # Salva o arquivo
                with open(file_name, "wb") as output_pdf:
                    writer.write(output_pdf)
    return tot_pags


if __name__ == '__main__':
    try:
        recibos_pagamentos_fortes()
    except Exception as e:
        print(e)
