import os
from PyPDF2 import PdfReader, PdfWriter
from sys import exit
from tqdm import tqdm

def rendimentos_fortes() -> int:
    tot_pags = 0
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    writer = PdfWriter()
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for file in files:
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b)
            tot_pags += len(pdf.pages)
            for page in tqdm(pdf.pages):
                rows = page.extract_text().split('\n')
                for i, row in enumerate(rows):
                    if 'Título de Eleitor' in row:
                        cpf = ''.join(char for char in row if char.isnumeric())
                        nome = rows[i+2]
                        break
                writer.add_page(page)
                if len(writer.pages) == 2:
                    file_name = f'Arquivos/{nome}-{cpf}.pdf'
                    with open(file_name, 'wb') as output:
                        writer.write(output)
                    writer = PdfWriter()
    return tot_pags


rendimentos_fortes()