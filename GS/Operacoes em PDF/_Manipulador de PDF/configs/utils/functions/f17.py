from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
import os


def f17() -> int:
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
                for i, row in enumerate(rows):
                    if ' CPF' in row:
                        row = row.split()
                        cpf = row[2]
                        nome = ' '.join(row[5:-1])
                        break
                writer.add_page(page)
                if len(writer.pages) == 2:
                    file_name = f'Arquivos/{nome}-{cpf}.pdf'
                    with open(file_name, 'wb') as output:
                        writer.write(output)
                    writer = PdfWriter()
    return tot_pags
