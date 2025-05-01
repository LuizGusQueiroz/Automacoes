from os import listdir, path, mkdir
from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm

# Cria a pasta de destino dos recibos
if not path.exists('Boletos'):
    mkdir('Boletos')

for arq in [file for file in listdir() if '.pdf' in file]:
    with open(arq, 'rb') as file:
        # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
        pdf_reader = PdfReader(file)

        # Itera sobre todas as páginas do PDF
        for page_pdf in tqdm(pdf_reader.pages):
            page = page_pdf.extract_text().split('\n')

            for row in page:
                if 'UF:CEP:Data Vencimento: ' in row:
                    condominio = row[row.rfind(':')+2:]
                    break
            for row in page:
                if 'Boleto referente:' in row:
                    numero = row[row.find(':')+1:row.find('/', row.find(' '))]
                    if len(numero) > 20:
                        numero = row[row.rfind(' ')+1:row.rfind('/')]
                    break

            nome_arq = f'{condominio}-{numero}.pdf'
            pdf_writer = PdfWriter()
            # Adiciona a página atual ao objeto PdfWriter
            pdf_writer.add_page(page_pdf)
            # Salva a página em um novo arquivo PDF
            with open(f'Boletos\\{nome_arq}', 'wb') as output_file:
                pdf_writer.write(output_file)
