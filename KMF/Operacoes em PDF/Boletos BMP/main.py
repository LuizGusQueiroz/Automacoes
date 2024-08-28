from PyPDF2 import PdfReader
from tqdm import tqdm
import os


def main():
    files = [file for file in os.listdir() if '.pdf' in file.lower()]

    for file in tqdm(files):
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b).pages[0]
            rows = pdf.extract_text().split('\n')
            row = rows[-2]
            nome = row[:row.find(' - CPF/CNPJ: ')]
        os.rename(file, f'BOLETO - {nome}.pdf')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        input()