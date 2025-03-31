import pymssql
from typing import Dict, List
from sys import exit
import pandas as pd
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from tqdm import tqdm
import shutil
import pikepdf


class Aut:
    def __init__(self, patterns: Dict[str, int] = {}):
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

    def get_rows(self, path: str):
        try:
            with open(path, 'rb') as file:
                rows = PdfReader(file).pages[0].extract_text().split('\n')
                return rows
        except FileNotFoundError:
            if not path.startswith('Y:\\'):
                return None
            new_path = path.replace('Y:\\CELULA FISCAL - FORTES', 'Z:')
            if new_path != path:
                return self.get_rows(new_path)
            return None
        except (PdfReadError, TypeError, KeyError, IndexError):
            return None

    def get_count(self) -> Dict[str, int]:
        count = {}
        paths = [str(path) for path in self.df['path'] if '.pdf' in str(path).lower()]
        for path in tqdm(paths):
            rows: List[str] = self.get_rows(path)
            if rows is None:
                continue
            i = 0
            while i+1 < len(rows) and len(rows[i].strip()) < 2:
                i += 1
            value = rows[i]
            if value in count.keys():
                count[value] += 1
            else:
                count[value] = 1
        return count

    def get_count_tipo(self) -> Dict[str, int]:
        """
            Retorna um dicionário com a contagem de cada tipo de arquivo, sendo as chaves do dicionário
        o tipo de arquivo, como '.pdf' e o valor, o total de ocorrências deste tipo.
        """
        count = {}
        for path in tqdm(self.df['path']):
            if path is None:
                end = 'None'
            else:
                end = path[path.rfind('.'):].lower()
            if end in count:
                count[end] += 1
            else:
                count[end] = 1
        return count

    def get_example(self, identificador: str, n: int=1):
        paths: List[str] = self.df['path'].unique().tolist()
        # Percorre todos os arquivos
        for path in tqdm(paths):
            rows: List[str] = self.get_rows(path)
            if rows is None:
                continue
            for i in range(min(len(rows), 3)):
                if rows[i] == identificador:
                    try:
                        shutil.copy(path, f'exemplo{n}.pdf')
                    except FileNotFoundError:
                        path = path.replace('Y:\\CELULA FISCAL - FORTES', 'Z:')
                        shutil.copy(path, f'exemplo{n}.pdf')
                    n -= 1
                    if n==0:
                        return
    def padrao_01(self, rows: List[str]) -> str:
        """
        Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
        Args:
            rows (List[str]): Lista de linhas da página do pdf.

        Returns:
            str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
        """
        for row in rows:
            if 'Nosso número' in row:
                beneficiario = row[row.find('Nosso número') + 12:]
            elif 'Espécie documento Aceite' in row:
                num_nf = row[:row.find('Espécie')]
            elif '(=) Valor do documento' in row:
                valor = row[:row.find('(=)')]
                break
        file_name = f'FOLK - {valor} - BOLETO - NF{num_nf} - {beneficiario}.pdf'

        return file_name

    def padrao_02(self, rows: List[str]) -> str:
        """
        Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
        Args:
            rows (List[str]): Lista de linhas da página do pdf.

        Returns:
            str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
        """
        num_nf = rows[1].split()[0]
        for i, row in enumerate(rows):
            if 'CONTROLE DO FISCODANFE' in row:
                beneficiario = row[22:]
            elif 'VALOR TOTAL DA NOTA' in row:
                valor = rows[i+1].split()[-1]
                break
        file_name = f'FOLK - {valor} - NF{num_nf} - {beneficiario}.pdf'
        return file_name

    def padrao_03(self, rows: List[str]) -> str:
        """
        Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
        Args:
            rows (List[str]): Lista de linhas da página do pdf.

        Returns:
            str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
        """
        beneficiario = rows[1]
        for row in rows:
            if '(=)' in row:
                num = row[row.find('Parcela') - 7:row.find('Parcela')]
            if 'R$' in row:
                valor = row.split()[1]
                break
        file_name = f'FOLK - {valor} - BOLETO - num{num} - {beneficiario}.pdf'
        return file_name

    def padrao_04(self, rows: List[str]) -> str:
        """
        Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
        Args:
            rows (List[str]): Lista de linhas da página do pdf.

        Returns:
            str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
        """
        for row in rows:
            if row.startswith('Número da Fatura:'):
                num = row.split()[-1]
            elif 'R$' in row:
                valor = row
                break
        file_name = f'FOLK - {valor} - BOLETO - num{num} - VIVO.pdf'
        return file_name

    def padrao_05(self, rows: List[str]) -> str:
        """
        Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
        Args:
            rows (List[str]): Lista de linhas da página do pdf.

        Returns:
            str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
        """
        beneficiario = None
        for i, row in enumerate(rows):
            if 'Competência daNFS-' in row:
                num = ''.join(char for char in row if char.isnumeric())
            elif 'Nome /Nome Empresarial' in row and beneficiario is None:
                beneficiario = ' '.join(rows[i + 1].split()[:-1])
            elif 'Valor Líquido' in row:
                valor = rows[i + 1]
        file_name = f'FOLK - {valor} - BOLETO - num{num} - {beneficiario}.pdf'
        return file_name

    def padrao_06(self, rows: List[str]) -> str:
        """
        Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
        Args:
            rows (List[str]): Lista de linhas da página do pdf.

        Returns:
            str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
        """
        beneficiario = rows[0]
        for row in rows:
            if 'Série:' in row:
                num = row.split(':')[1]
                break
        for row in rows:
            if 'R$' in row:
                valor = row[row.rfind(':') + 2:]
                break
        file_name = f'FOLK - {valor} - NF{num} - {beneficiario}.pdf'
        return file_name

    def padrao_07(self, rows: List[str]) -> str:
        """
        Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
        Args:
            rows (List[str]): Lista de linhas da página do pdf.

        Returns:
            str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
        """
        beneficiario = rows[1]
        for row in rows:
            if 'R$' in row:
                valor = row
                break
        file_name = f'FOLK - {valor} - BOLETO - {beneficiario}.pdf'
        return file_name

    def padrao_08(self, rows: List[str]) -> str:
        """
        Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
        Args:
            rows (List[str]): Lista de linhas da página do pdf.

        Returns:
            str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
        """
        for i, row in enumerate(rows):
            if 'R$' in row:
                row = rows[i + 1]
                beneficiario = ' '.join(row.split()[3:])[2:]
                valor = row.split()[2]
                valor = valor[:valor.find(',') + 3]
                break

        file_name = f'FOLK - {valor} - BOLETO - {beneficiario}.pdf'
        return file_name

    def padrao_09(self, rows: List[str]) -> str:
        """
        Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
        Args:
            rows (List[str]): Lista de linhas da página do pdf.

        Returns:
            str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
        """
        beneficiario = rows[2][:-15]
        num = rows[3]

        for i, row in enumerate(rows):
            if 'Valor Líquido' in row:
                valor = rows[i + 1]
                break
        file_name = f'FOLK - {valor} - NF{num} - {beneficiario}.pdf'
        return file_name

    def run(self) -> None:
        # Lista todos os códigos de pedido.
        codigos = self.df['ped_codigo'].unique()
        # Percorre todos os códigos.
        for codigo in tqdm(codigos):
            # Lista todos os caminhos de arquivos atrelados a este código.
            paths = self.df[self.df['ped_codigo'] == codigo]['path']
            for path in paths:
                rows: List[str] = self.get_rows(path)
                if rows is None:
                    continue
                """
                    Identifica o tipo de arquivo através do padrão da primeira ou segunda linha.
                    O min(2, len(rows)) previso o caso de pdfs baseados em imagem, que contém apenas uma linha.
                    O max() serve para pegar apenas o padrão encontrado, que sempre será superior que 0.
                """
                padrao = max(self.patterns.get(rows[i], 0) for i in range(min(2, len(rows))))
                if padrao == 0:  # Caso não seja encontrado nenhuma correspondência, o arquivo é ignorado.
                    continue
                print([path, padrao])
                file_name = eval(f'self.padrao_{padrao:02}(rows)')
                file_name = f'Arquivos/{file_name}'
                print(['file_name', file_name])
                #shutil.copy(path, file_name)

                """
                    Pode ocorrrer de o arquivo ter sido removido do diretório mas não do sistema, e ao tentar acessá-lo,
                gerar erro, ou o pdf pode estar em um formato inválido ou corrompido, gerando erros também.
                """



patterns: Dict[str, int] = {
    'Local de pagamento': 1,
    'RECEBEMOS DE SIMPLES SOLUTIONS COME DE EQUIP ELETRONICOS LTDA OS PRODUTOS CONSTANTES DA NOTA FISCAL INDICADO AO LADONF-e': 2,
    'Banco do Brasil S/A 001-9Beneficiário': 3,
    'Telefônica Brasil S/A': 4,
    'DANFSe v1.0': 5,
    'WERUS METALÚRGICA E MANUTENÇÕES': 6,
    'Seu boleto chegou,': 7,
    'Local de Pagamento': 8,
    '1 /': 9
}


if __name__ == '__main__':
    try:
        aut = Aut(patterns)
        #aut.run()
        #count = aut.get_count()
        aut.get_example('RECEBEMOS DE SIMPLES SOLUTIONS COME DE EQUIP ELETRONICOS LTDA OS PRODUTOS CONSTANTES DA NOTA FISCAL INDICADO AO LADONF-e', 3)
        #count = aut.get_count_tipo()
        # for key in count:
        #     print(f'{key}: {count[key]}')

    except Exception as e:
        print(e)
        input()
