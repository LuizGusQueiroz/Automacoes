from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
import os


def f14() -> int:
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
