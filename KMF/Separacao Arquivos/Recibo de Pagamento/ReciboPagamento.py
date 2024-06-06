from os import listdir, path, mkdir
from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm

# Cria a pasta de destino dos recibos
if not path.exists('Recibos'):
    mkdir('Recibos')

escolha = ''
while escolha not in ['1', '2']:
    escolha = input('---------------\n'
                    '1: Separar por funcionário.\n'
                    '2: Separar por Lotação.\n'
                    'Escolha: ')

files = [file for file in listdir() if '.pdf' in file]

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
                lotacao = rows[9][6:-5]
                file_name = f'Recibos\\{lotacao}-{nome}.pdf'
                pdf_writer = PdfWriter()
                # Adiciona a página atual ao objeto PdfWriter
                pdf_writer.add_page(pag)

                # Salva a página em um novo arquivo PDF
                with open(file_name, 'wb') as output_file:
                    pdf_writer.write(output_file)

        elif escolha == '2':  # Separa por lotação
            for pag in tqdm(pdf_reader.pages):
                rows = pag.extract_text().split('\n')
                lotacao = rows[9][6:-5]

                file_name = f'Recibos\\{lotacao}.pdf'
                pdf_writer = PdfWriter()
                # Verifica se já existe um arquivo para esta lotação.
                if path.exists(file_name):
                    pdf_reader_temp = PdfReader(file_name)
                    # Copia todas as páginas do documento da lotação para o writer.
                    for page_num in range(len(pdf_reader_temp.pages)):
                        pdf_writer.add_page(pdf_reader_temp.pages[page_num])
                # Adiciona a página atual
                pdf_writer.add_page(pag)
                # Salva o arquivo
                with open(file_name, "wb") as output_pdf:
                    pdf_writer.write(output_pdf)