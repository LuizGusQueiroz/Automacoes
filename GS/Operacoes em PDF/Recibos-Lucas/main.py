from os import listdir, path, mkdir
from PyPDF2 import PdfReader
from tqdm import tqdm
import pandas as pd


if not path.exists('Planilhas'):
    mkdir('Planilhas')

for arq in [file for file in listdir() if '.pdf' in file]:
    df = pd.DataFrame(columns=['Empregado', 'Total'])
    with open(arq, 'rb') as file:
        # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF.
        pdf_reader = PdfReader(file)
        dados = list()
        achou = False
        for pag in tqdm(pdf_reader.pages):

            rows = pag.extract_text().split('\n')
            for i, row in enumerate(rows):
                # Acessa o nome do contrato e do empregado.
                if row == 'Total':
                    if not rows[i-2].startswith(' '):
                        contrato = rows[i-2]
                    achou = True
                    nome = rows[i-1].split()[1:]
                    idx = 0
                    while nome[idx].isalpha():
                        idx += 1
                    nome = ' '.join(nome[:idx])
                if achou and row.startswith(' '):
                    achou = False
                    total = row.split()[0]
                    df.loc[len(df)] = [nome, total]
    df.to_excel(f'Planilhas\\{arq.replace('.pdf', '.xlsx')}', index=False)

