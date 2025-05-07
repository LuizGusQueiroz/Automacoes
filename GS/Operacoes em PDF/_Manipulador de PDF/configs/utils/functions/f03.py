from PyPDF2 import PdfReader
from tqdm import tqdm
import os


def f03() -> int:
    # Cria a pasta de destino dos documentos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    tot_pags: int = 0
    # Itera por todos os arquivos .pdf.
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for file in tqdm(files):
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b).pages[0]
            rows = pdf.extract_text().split('\n')
            row = rows[-2]
            nome = row[:row.find(' - CPF/CNPJ: ')]
            tot_pags += len(PdfReader(file_b).pages)
        os.rename(file, f'Arquivos/BOLETO - {nome}.pdf')
    return tot_pags
