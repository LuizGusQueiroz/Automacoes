from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
import os


def f16() -> int:
    n_pags = 0
    if not os.path.exists('Cartas'):
        os.mkdir('Cartas')
    files = [file for file in os.listdir() if '.pdf' in file.lower()]

    for file in files:
        writer = PdfWriter()
        primeiro = True
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b)
            n_pags += len(pdf.pages)
            for page in tqdm(pdf.pages):
                rows = page.extract_text().split('\n')
                nome = rows[1].replace('/', '')
                if rows[0] == 'Prezados, ' and not primeiro:
                    with open(f'Cartas/{nome}.pdf', 'wb') as output:
                        writer.write(output)
                    writer = PdfWriter()
                writer.add_page(page)
                primeiro = False
    return n_pags