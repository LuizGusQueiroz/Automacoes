import pandas as pd
import datetime
from os import listdir


def run(file: str) -> None:
    df = pd.read_excel(file).fillna('')

    # Encontra as colunas necessárias
    col_desp = ''
    col_empr = ''
    col_desc = ''
    col_entr = ''
    col_saida = ''
    col_saldo = ''
    index = 0
    while df['Razão'].iloc[index] != 'Data':
        index += 1

    for coluna in df.columns:
        if df[coluna].iloc[index] == 'Seq.':
            col_desp = coluna
        elif df[coluna].iloc[index] == 'Histórico':
            col_desc = coluna
        elif df[coluna].iloc[index] == 'Entrada':
            col_entr = coluna
        elif df[coluna].iloc[index] == 'Saída':
            col_saida = coluna
        elif df[coluna].iloc[index] == 'Saldo':
            col_saldo = coluna

    col_empr = f'{col_desp[:-1]}{int(col_desp[-1]) + 1}'

    df = df[['Razão', 'Unnamed: 1', col_desp, col_empr, col_desc, col_entr, col_saida, col_saldo]]
    df.columns = ['Razão', 'Rec/Desp:', 'Despesa', 'Empresa', 'Desc', 'Entrada', 'Saída', 'Saldo']

    # Salva apenas as linhas necessárias
    mask = [False] * df.shape[0]

    for row in range(df.shape[0]):
        item = df['Razão'].iloc[row]
        if type(item) == datetime.datetime:
            mask[row] = True
            # Junta o texto das linhas abaixo
            index = row + 1
            while index < df.shape[0] and type(df['Razão'].iloc[index]) != datetime.datetime:
                df.at[row, 'Desc'] += f" {df['Desc'].iloc[index]}"
                index += 1
        elif item == 'Estabelecimento:':
            mask[row] = True
        else:
            item = df['Rec/Desp:'].iloc[row]
            if item == 'Rec/Desp:':
                mask[row] = True

    df = df[mask].reset_index(drop=True)

    # Copia os nomes dos estabelecimentos e despesas nas linhas abaixo
    estabelecimento = ''
    despesa = ''
    for row in range(df.shape[0]):
        item = df['Razão'].iloc[row]
        if type(item) == datetime.datetime:
            df.at[row, 'Despesa'] = despesa
            df.at[row, 'Empresa'] = estabelecimento
        elif item == 'Estabelecimento:':
            estabelecimento = df['Empresa'].iloc[row]
        elif df['Rec/Desp:'].iloc[row] == 'Rec/Desp:':
            despesa = despesa = df['Despesa'].iloc[row]

    # Pega apenas as linhas que tem as descrições de despesas
    mask = [False] * df.shape[0]
    for row in range(df.shape[0]):
        item = df['Razão'].iloc[row]
        if type(item) == datetime.datetime:
            mask[row] = True

    df = df[mask]
    # Larga a coluna Rec/Desp
    df = df.drop('Rec/Desp:', axis='columns')

    # Corrige o formato de datas
    df['Razão'] = df['Razão'].apply(lambda x: x.strftime('%d/%m/%Y'))

    df.to_excel(f'{file.replace('.xls', 
                                '-Corrigido.xlsx')}', index=False)


files = [file for file in listdir() if '.xls' in file]
for file in files:
    try:
        run(file)
    except Exception as e:
        print(f'Erro em: {file}')