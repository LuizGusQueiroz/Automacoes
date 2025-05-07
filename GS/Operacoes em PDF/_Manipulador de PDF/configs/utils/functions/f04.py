from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
import os


def f04() -> int:
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
