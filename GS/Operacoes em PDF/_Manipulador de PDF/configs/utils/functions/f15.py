from PyPDF2 import PdfReader
from tqdm import tqdm
import os


def f15() -> int:
    n_pags = 0
    files = [file for file in os.listdir() if '.pdf' in file.lower()]

    for file in tqdm(files):
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b)
            n_pags += len(pdf.pages)
            rows = pdf.pages[0].extract_text().split('\n')
            nome = rows[-3].split('Endereço')[-1]
            cnpj = ''.join([char for char in rows[-1].split()[0] if char.isnumeric()])
            nome_arq = f'{nome}-{cnpj}.pdf'
        os.rename(file, nome_arq)
    return n_pags
