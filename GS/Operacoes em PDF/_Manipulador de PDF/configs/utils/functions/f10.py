from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
import os


def f10() -> int:
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    tot_pags: int = 0

    files = [file for file in os.listdir() if '.pdf' in file.lower()]

    for file in files:
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file)
        tot_pags += len(pdf.pages)
        for page in tqdm(pdf.pages):
            rows = page.extract_text().split('\n')
            nome = rows[1][rows[1].find('.')+1:]
            writer = PdfWriter()
            writer.add_page(page)
            with open(f'Arquivos/RECIBO - {nome}.pdf', 'wb') as output:
                writer.write(output)
    return tot_pags
