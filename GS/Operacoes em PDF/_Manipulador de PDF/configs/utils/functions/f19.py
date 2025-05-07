from PyPDF2 import PdfReader
from tqdm import tqdm
import pandas as pd
import os


def eh_dependente(row: str) -> bool:
    return ',' not in row.split()[0]


def f19() -> int:
    tot_pags = 0
    df = pd.DataFrame(columns=['Empresa', 'Lotação', 'Operador', 'Plano', 'Nome',
                               'Dependente', 'Valor Funcionário', 'Valor Empresa'])
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for file in files:
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b)
            tot_pags += len(pdf.pages)
            for page in tqdm(pdf.pages):
                rows = page.extract_text().split('\n')
                empresa = ' '.join(rows[1].split()[1:])
                operador = rows[3][10:]
                lotacao = rows[6]

                for i, row in enumerate(rows[7:-1], start=7):
                    if '-' in row:
                        if ' Total: ' in row:
                            continue
                        row = row.split()
                        plano = ' '.join(row[3:-2])
                        ii = i - 1
                        # Busca a linha com o nome do funcionário.
                        while ('-' in rows[ii]) or eh_dependente(rows[ii]):
                            ii -= 1

                        nome = ' '.join(rows[ii].split()[3:-2])
                        valor_fun = row[0]
                        valor_emp = row[1]
                        df.loc[len(df)] = [empresa, lotacao, operador, plano, nome, '', valor_fun, valor_emp]
                        ii = i + 1
                        while eh_dependente(rows[ii]):
                            row = rows[ii].split()
                            nome_dep = ' '.join(row[1:-5])
                            valor_fun = row[-5]
                            valor_emp = row[-4]
                            df.loc[len(df)] = [empresa, lotacao, operador, plano, nome, nome_dep, valor_fun, valor_emp]
                            ii += 1
            # Cálculo dos totais.
            df['é dependente'] = df['Dependente'].apply(lambda x: ['Não', 'Sim'][bool(x)])
            df['Valor Funcionário'] = df['Valor Funcionário'].apply(lambda x: float(x.replace(',', '.')))
            df['Valor Empresa'] = df['Valor Empresa'].apply(lambda x: float(x.replace(',', '.')))
            df_totais = df.groupby(['Empresa', 'Plano', 'é dependente'])[['Valor Funcionário', 'Valor Empresa']].sum().reset_index()
            df_totais['Total Funcionários'] = df.groupby(['Empresa', 'Plano', 'é dependente'])['Nome'].nunique().values
            df_totais['Total Dependentes'] = df.groupby(['Empresa', 'Plano', 'é dependente'])['Dependente'].nunique().values
            for row in range(len(df_totais)):
                if df_totais['é dependente'].iloc[row] == 'Não':
                    df_totais.at[row, 'Total Dependentes'] = 0
                else:
                    df_totais.at[row, 'Total Funcionários'] = 0
            # Calcula a soma dos totais.
            df_totais.loc[len(df_totais)] = ['TOTAIS', '', '',
                                             df_totais['Valor Funcionário'].sum(), df_totais['Valor Empresa'].sum(),
                                             df_totais['Total Funcionários'].sum(), df_totais['Total Dependentes'].sum()]
            df.to_excel('planos.xlsx', index=False)
            df_totais.to_excel('totais.xlsx', index=False)
    return tot_pags
