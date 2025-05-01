import os
from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
from sys import exit
from typing import List
import pandas as pd

diretorios = []

def get_diretorios(path: str = None, i: int = 0) -> None:
    files = os.listdir(path)
    if any(['.pdf' in file for file in files]):
        diretorios.append(path)
    for file in files:
        print('-'*i, file)
        new_path = file if (path is None) else f'{path}/{file}'
        if os.path.isdir(new_path):
            get_diretorios(new_path, i+1)


def planos_de_saude() -> int:
    def eh_dependente(row: List[str]) -> bool:
        return ',' in row[0]

    tot_pags = 0
    df = pd.DataFrame(columns=['Lotação', 'Operador', 'Plano', 'Nome',
                               'Responsável', 'Valor-Fun', 'Valor-Emp'])
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for file in files:
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b)
            tot_pags += len(pdf.pages)
            for page in tqdm(pdf.pages):
                rows = page.extract_text().split('\n')
                operador = rows[3][10:]
                lotacao = rows[6]

                for i, row in enumerate(rows[7:-1], start=7):
                    if '-' in row:
                        row = row.split()
                        plano = ' '.join(row[3:-2])
                        ii = i - 1
                        # Busca a linha com o nome do funcionário.
                        while ('-' in rows[ii]) or eh_dependente(rows[ii]):
                            ii -= 1

                        nome = ' '.join(rows[ii].split()[3:-2])
                        valor_fun = row[0]
                        valor_emp = row[1]
                        df.loc[len(df)] = [lotacao, operador, plano, nome, '', valor_fun, valor_emp]
                        ii = i + 1
                        while eh_dependente(rows[ii]):
                            nome_dep = ' '.join(rows[ii].split()[1:-5])
                            valor_fun = rows[ii][-5]
                            valor_emp = rows[ii][-4]
                            df.loc[len(df)] = [lotacao, operador, plano, nome, nome_dep, valor_fun, valor_fun, valor_emp]
                df.to_excel('t.xlsx', index=False)
                exit()
                #     if '-' in row:
                #         tipo = ' '.join(row.split()[3:-2])




planos_de_saude()

