from os import listdir, path, mkdir, rename, getcwd, remove
from PyPDF2 import PdfReader, PdfWriter

# Cria a pasta de destino dos recibos
if not path.exists('Recibos'):
    mkdir('Recibos')

files = [file for file in listdir() if '.pdf' in file]

for arq in files:
    with open(arq, 'rb') as file:
        # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
        pdf_reader = PdfReader(file)

        # Itera sobre todas as páginas do PDF
        for i in range(len(pdf_reader.pages)):
            pag = pdf_reader.pages[i].extract_text().split('\n')
            # Acessa a linha que contém o nome do empregado.
            nome = pag[11]

            pdf_writer = PdfWriter()

            # Adiciona a página atual ao objeto PdfWriter
            pdf_writer.add_page(pdf_reader.pages[i])

            # Salva a página em um novo arquivo PDF
            with open(f'Recibos\\{nome}.pdf', 'wb') as output_file:
                pdf_writer.write(output_file)

