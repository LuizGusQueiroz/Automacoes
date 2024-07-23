import pandas as pd
from sys import exit
import os


def separa_parquet_incremental(path: str, destino: str, tamanho_pedaco: int = 30000):
    # Carregar o arquivo Parquet original para um DataFrame
    df_original = pd.read_parquet(path)

    particoes_completas = len(os.listdir(destino))
    # Verifica se a última partição está incompleta
    if os.listdir(destino):
        ultimo_parquet = pd.read_parquet(f'destino/{sorted(os.listdir(destino))[-1]}')
        if ultimo_parquet.shape != (tamanho_pedaco, 3):
            n_linhas = ultimo_parquet.shape[0]
            particoes_completas -= 1
            # Descarta as linhas desnecessárias
            df_original = df_original.iloc[tamanho_pedaco*particoes_completas+n_linhas:].reset_index(drop=True)
            ultimo_parquet = pd.concat([ultimo_parquet, df_original.iloc[:tamanho_pedaco-n_linhas]])
            nome_arquivo = os.path.join(destino, f'particao_{particoes_completas:04}.parquet')
            ultimo_parquet.to_parquet(nome_arquivo, index=False, engine='pyarrow')
            # Descarta as demais linhas do df principal
            df_original = df_original.iloc[tamanho_pedaco-n_linhas:]
            particoes_completas += 1

    # Dividir o DataFrame original em pedaços menores
    pedacos = [df_original[i:i + tamanho_pedaco] for i in range(0, len(df_original), tamanho_pedaco)]

    # Salvar cada pedaço como um arquivo Parquet separado na pasta de destino
    for idx, pedaco in enumerate(pedacos, start=particoes_completas):
        nome_arquivo = os.path.join(destino, f'particao_{idx:04}.parquet')

        if os.path.exists(nome_arquivo):
            os.remove(nome_arquivo)

        pedaco.to_parquet(nome_arquivo, index=False, engine='pyarrow')

    print(f'Arquivos particionados salvos em: {destino}')


if __name__ == '__main__':
    try:
        separa_parquet_incremental(
            # path=r"C:\Users\ADM\OneDrive - KMF - CONSULTORIA EMPRESARIAL E TREINAMENTOS LTDA - ME\HISEG - Sharepoint\somaseg_alarmes\output.parquet",
            # destino=r"C:\Users\ADM\OneDrive - KMF - CONSULTORIA EMPRESARIAL E TREINAMENTOS LTDA - ME\HISEG - Sharepoint\somaseg_alarmes\alarmes_parquet"
            path=r'output.parquet',
            destino='destino'
        )
    except Exception as e:
        print(e)

