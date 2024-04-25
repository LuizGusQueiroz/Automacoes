import pandas as pd
import datetime
from os import listdir


def run(path, grupo: str):
    df = pd.read_excel(path).fillna('')
    de_para = pd.read_excel(f'{grupo}.xlsx').fillna('')
    # Encontra as colunas necessárias

    print(df.iloc[6:10])
    x = input('clie, ent, saida: ').split()

    col_desp = df.columns[3]
    col_empr = df.columns[4]
    col_desc = df.columns[2]

    col_clie = df.columns[int(x[0])]
    col_entr = df.columns[int(x[1])]
    col_saida = df.columns[int(x[2])]

    df = df[['Razão', 'Unnamed: 1', col_desp, col_empr,
             col_desc, col_clie, col_entr, col_saida]]
    df.columns = ['Razão', 'Rec/Desp:', 'Despesa', 'Empresa',
                  'Desc', 'Cliente/Fornecedor', 'Entrada', 'Saída']

    # Cria novas colunas que serão usadas.
    df['GRUPO'] = [grupo] * df.shape[0]
    df['Código'] = [''] * df.shape[0]
    df['TOTAL'] = [''] * df.shape[0]
    df['COD-DRE'] = [''] * df.shape[0]
    # Salva apenas as linhas necessárias
    mask = [False] * df.shape[0]

    for row in range(df.shape[0]):
        item = df['Razão'].iloc[row]
        if type(item) == datetime.datetime:
            mask[row] = True
            # Junta o texto das linhas abaixo
            index = row + 1
            while index < df.shape[0] and type(df['Razão'].iloc[index]) != datetime.datetime:
                df.at[row, 'Cliente/Fornecedor'] += f" {df['Cliente/Fornecedor'].iloc[index]}"
                index += 1
        elif item == 'Estabelecimento:':
            mask[row] = True
        else:
            item = df['Rec/Desp:'].iloc[row]
            if item == 'Rec/Desp:':
                mask[row] = True

    df = df[mask].reset_index(drop=True)
    # Preenche os dados do estabelecimento e despesas nas linhas abaixo.
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

    for row in range(df.shape[0]):
        item = df['Despesa'].iloc[row]
        df.at[row, 'Código'] = item[:item.find(' - ')]
        df.at[row, 'Despesa'] = item[item.find(' - ') + 3:]

    df = df[mask].reset_index(drop=True)

    # Corrige o formato de datas
    df['Data'] = df['Razão'].apply(lambda x: x.strftime('%d/%m/%Y'))
    df['Competência'] = df['Razão'].apply(lambda x: x.strftime('%m/%Y'))
    df['Ano'] = df['Razão'].apply(lambda x: x.strftime('%Y'))

    # Soma os valores da coluna entrada com saída para a coluna total.
    for row in range(df.shape[0]):
        v1 = str(df['Entrada'].iloc[row]).replace(',', '.')
        v2 = str(df['Saída'].iloc[row]).replace(',', '.')
        df.at[row, 'TOTAL'] = float(v1) + float(v2)
    # Acessa o de_para para preencher a coluna 'CÓD-DRE'.
    for row in range(df.shape[0]):
        cod = df['Código'].iloc[row]
        cod_dre = de_para['CÓD-DRE'][de_para['CÓD.'] == int(cod)].to_list()[0]
        df.at[row, 'COD-DRE'] = cod_dre

    # Reordena as colunas
    df = df[['GRUPO', 'Empresa', 'Ano', 'Competência', 'Data', 'COD-DRE', 'Código', 'Despesa',
             'Cliente/Fornecedor', 'Desc', 'Entrada', 'Saída', 'TOTAL', ]]

    # Cria linhas em branco para meses ausentes
    df['Comp-Datetime'] = df['Competência'].apply(
        lambda x: datetime.datetime.strptime(x, '%m/%Y'))
    empresas = df['Empresa'].unique()
    for empresa in empresas:
        df_emp = df[df['Empresa'] == empresa]
        comps = sorted(df_emp['Comp-Datetime'].unique())
        comps = [comp.strftime('%m/%Y') for comp in comps]
        comp = comps[0]
        while comp != comps[-1]:
            mes = int(comp[:2])
            if mes < 12:
                mes += 1
                comp = f'{mes:02}{comp[2:]}'
            else:
                ano = int(comp[3:]) + 1
                comp = f'01/{ano}'
            # Verifica se essa competência existe para este mês
            if not df[(df['Empresa'] == empresa) & (df['Competência'] == comp)].shape[0]:
                row = [grupo, empresa, comp[3:], comp, '', 1, '', '', '', '', 0, 0, 0, '']
                df.loc[len(df)] = row

    df = df[['GRUPO', 'Empresa', 'Ano', 'Competência', 'Data', 'COD-DRE', 'Código', 'Despesa',
             'Cliente/Fornecedor', 'Desc', 'Entrada', 'Saída', 'TOTAL', ]]

    df.to_excel(path.replace('.xls', '-Corrigido.xlsx'), index=False)


grupo = 'GESTART'
files = [file for file in listdir() if '.xls' in file and file != f'{grupo}.xlsx']

for file in files:
    run(file, grupo)
