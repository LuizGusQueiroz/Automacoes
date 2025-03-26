import pymssql
from typing import Dict, List
from sys import exit
import pandas as pd
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from tqdm import tqdm
import shutil


class Aut:
    def __init__(self, patterns: Dict[str, str] = {}):
        self.patterns = patterns
        self.creds: Dict[str, str] = self.get_creds()
        self.df: pd.DataFrame = self.get_data()

    def get_creds(self) -> Dict[str, str]:
        with open('creds.txt', 'r') as file:
            rows: List[str] = file.read().split('\n')
            rows: List[List[str]] = [row.split(' = ') for row in rows]
            creds = {chave: valor for chave, valor in rows}
        return creds

    def get_data(self) -> pd.DataFrame:
        try:
            # Cria a conexão.
            conn = pymssql.connect(server=self.creds['server'], user=self.creds['user'],
                                   password=self.creds['password'], database=self.creds['database'])
            # Cria o cursor.
            cursor = conn.cursor()
            # Realiza a consulta da tabela da pedidos.
            cursor.execute('SELECT PED_codigo, Path FROM DPE')
            """
                Criação de uma lista que irá guardar os resultados da consulta, onde cada item do dicionário será
            um dicionário, com as chaves 'ped_codigo', que é o código do pedido, e 'path' que é o caminho até o arquivo
            referente ao pedido.
            """
            data = []
            for row in cursor.fetchall():
                data.append({'ped_codigo': row[0], 'path': row[1]})
            # A lista de dicionários é convertida para um DataFrame para melhor manipulação.
            # O DataFrame tem as colunas 'ped_codigo' e 'path'.
            df = pd.DataFrame(data)
            # Encerrando a conexão
            conn.close()
            cursor.close()

            return df
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def get_count(self) -> Dict[str, int]:
        count = {}
        for path in tqdm(self.df['path']):
            try:
                with open(path, 'rb') as file:
                    pdf = PdfReader(file)
                    rows = pdf.pages[0].extract_text().split('\n')
                    i = 0
                    while i+1 < len(rows) and len(rows[i].strip()) < 2:
                        i += 1
                    value = rows[i]
                    if value in count.keys():
                        count[value] += 1
                    else:
                        count[value] = 1
            except (FileNotFoundError, TypeError, PdfReadError):
                pass
        return count

    def get_example(self, identificador: str):
        paths: List[str] = self.df['path'].unique().tolist()
        # Percorre todos os arquivos
        for path in tqdm(paths):
            try:
                with open(path, 'rb') as file:
                    pdf = PdfReader(file)
                    rows: List[str] = pdf.pages[0].extract_text().split('\n')
                    for i in range(min(len(rows), 3)):
                        if rows[i] == identificador:
                            shutil.copy(path, 'exemplo.pdf')
                            return
            except (FileNotFoundError, TypeError, PdfReadError):
                pass

    def run(self) -> None:
        # Lista todos os códigos de pedido.
        codigos = self.df['ped_codigo'].unique()
        # Percorre todos os códigos.
        for codigo in tqdm(codigos):
            # Lista todos os caminhos de arquivos atrelados a este código.
            paths = self.df[self.df['ped_codigo'] == codigo]['path']
            for path in paths:
                try:
                    with open(path, 'rb') as file:
                        pdf = PdfReader(path)
                        # Extrai o texto do pdf e o separa por linha, considerando apenas a primeira linha.
                        rows: List[str] = pdf.pages[0].extract_text().split('\n')
                        """
                            Identifica o tipo de arquivo através do padrão da primeira ou segunda linha.
                            O min(2, len(rows)) previso o caso de pdfs baseados em imagem, que contém apenas uma linha.
                            O max() serve para pegar apenas o padrão encontrado, que sempre será superior que 0.
                        """
                        padrao = max(self.patterns.get(rows[i], 0) for i in range(min(2, len(rows))))
                        if padrao == 0:  # Caso não seja encontrado nenhuma correspondência, o arquivo é ignorado.
                            continue
                        file_name = exec(f'self.padrao_{padrao}(rows)')
                        file_name = f'Arquivos/{file_name}'
                        shutil.copy(path, file_name)

                    """
                        Pode ocorrrer de o arquivo ter sido removido do diretório mas não do sistema, e ao tentar acessá-lo,
                    gerar erro, ou o pdf pode estar em um formato inválido ou corrompido, gerando erros também.
                    """
                except (FileNotFoundError, TypeError, PdfReadError):
                    pass


try:
    aut = Aut()
    #aut.run()
    #count = aut.get_count()
    aut.get_example('Seu boleto chegou,')
except Exception as e:
    print(e)
    input()
