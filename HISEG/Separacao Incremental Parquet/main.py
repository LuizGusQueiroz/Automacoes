import pandas as pd
from sys import exit
import os


def separa_parquet_incremental(path: str, destino: str, tamanho_pedaco: int = 30000):
    # Carregar o arquivo Parquet original para um DataFrame
    df_original = pd.read_parquet(path)

    # Dividir o DataFrame original em pedaços menores
    pedacos = [df_original[i:i + tamanho_pedaco] for i in range(0, len(df_original), tamanho_pedaco)]

    # Salvar cada pedaço como um arquivo Parquet separado na pasta de destino
    for idx, pedaco in enumerate(pedacos):
        nome_arquivo = os.path.join(destino, f'particao_{idx:04}.parquet')

        if os.path.exists(nome_arquivo):
            os.remove(nome_arquivo)

        pedaco.to_parquet(nome_arquivo, index=False, engine='pyarrow')

    print(f'Arquivos particionados salvos em: {destino}')


if __name__ == '__main__':
    print(pd.read_parquet.__doc__)
    exit()
    try:
        separa_parquet_incremental(
            # path=r"C:\Users\ADM\OneDrive - KMF - CONSULTORIA EMPRESARIAL E TREINAMENTOS LTDA - ME\HISEG - Sharepoint\somaseg_alarmes\output.parquet",
            # destino=r"C:\Users\ADM\OneDrive - KMF - CONSULTORIA EMPRESARIAL E TREINAMENTOS LTDA - ME\HISEG - Sharepoint\somaseg_alarmes\alarmes_parquet"
            path=r'output.parquet',
            destino='destino'
        )
    except Exception as e:
        print(e)

