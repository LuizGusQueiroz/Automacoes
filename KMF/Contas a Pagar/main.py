import os.path

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
        except (PdfReadError, TypeError, KeyError, IndexError, OSError):
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
        paths: List[str] = self.df['path'].unique().tolist()[::-1]
        # Percorre todos os arquivos
        for path in tqdm(paths[::-1]):
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
        if rows[2].startswith('Pagar preferencialmente'):
            # Subpadrão 1
            for row in rows:
                if 'Nosso número' in row:
                    beneficiario = row[row.find('Nosso número') + 12:]
                elif 'Espécie documento Aceite' in row:
                    num = row[:row.find('Espécie')]
                elif '(=) Valor do documento' in row:
                    valor = row[:row.find('(=)')]
                    break
        elif rows[2].startswith('Até o vencimento'):
            # Subpadrão 2
            beneficiario = None
            for i, row in enumerate(rows):
                num = ''
                if 'Beneﬁciário' in row and beneficiario is None:
                    beneficiario = rows[i + 1][:-5]
                elif '(=) Valor do documento' in row:
                    valor = rows[i + 1]
                    break
        elif rows[2].startswith('Pagável Preferencialmente'):
            for i, row in enumerate(rows):
                if 'Beneficiário' in row:
                    row = rows[i + 1]
                    beneficiario = row[:row.find('Agência/Código')]
                elif 'Espécie doc' in row:
                    num = row[:row.find('Espécie doc')].replace('/', '')
                elif '(=) Valor do Documento' in row:
                    valor = rows[i + 1]
                    break
        file_name = f'FOLK - {valor} - BOLETO - NF{num} - {beneficiario}.pdf'

        return file_name

    def padrao_02(self, rows: List[str]) -> str:
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
        for row in rows:
            if row.startswith('Número da Fatura:'):
                num = row.split()[-1]
            elif 'R$' in row:
                valor = row
                break
        file_name = f'FOLK - {valor} - BOLETO - num{num} - VIVO.pdf'
        return file_name

    def padrao_05(self, rows: List[str]) -> str:
        if 'Página' in rows[2]:
            # Subpadrão 2
            for i, row in enumerate(rows):
                if 'Nome / Nome Empresarial' in row:
                    row = rows[i + 1]
                    beneficiario = row[:row.rfind('.')]
                elif 'Competência da NFS-e' in row:
                    num = row[:row.find('C')]
                elif 'Valor do Serviço' in row:
                    row = rows[i + 1]
                    valor = row[:row.find(',') + 3]
                    break
        else:
            # Subpadrão 1
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
        beneficiario = rows[1]
        for row in rows:
            if 'R$' in row:
                valor = row
                break
        file_name = f'FOLK - {valor} - BOLETO - {beneficiario}.pdf'
        return file_name

    def padrao_08(self, rows: List[str]) -> str:
        if 'Local de Pagamento' in rows[0] and 'Beneficiário' in rows[1]:  # subpadrão 1
            for i, row in enumerate(rows):
                if 'R$' in row:
                    row = rows[i + 1]
                    beneficiario = ' '.join(row.split()[3:])[2:]
                    valor = row.split()[2]
                    valor = valor[:valor.find(',') + 3]
                    row = rows[i + 2]
                    num = row.split()[2]
                    num = num[num.find('/') - 4:num.find('/') + 2]
                    break
        elif 'Recibo do Sacado' in rows[0]:
            # subpadrao 2
            for i, row in enumerate(rows):
                if 'Espécie Doc' in row:
                    num = row.split()[0]
                elif 'Valor do Documento' in row:
                    valor = rows[i + 1].strip()
                elif row.startswith('Sacado'):
                    beneficiario = ' '.join(row.split()[1:-3])
                    break
        elif 'Recibo do Pagador' in rows[0]:
            # subpadrão 4
            beneficiario = None
            for i, row in enumerate(rows):
                if 'Beneficiário' in row and beneficiario is None:
                    beneficiario = ' '.join(row.split()[1:-3])
                elif 'Especie Doc.' in row:
                    num = row[:row.find('Especie Doc.')]
                elif 'Valor do Documento' in row:
                    valor = rows[i + 1]
                    break
        elif 'Local de Pagamento' in rows[0]:
            # Subpadrão 5
            num = rows[-1]
            for i, row in enumerate(rows):
                if '(=) Valor do documento' in row:
                    valor = row.split()[-4][:-2]
                elif '(+) Outros Acréscimos' in row:
                    beneficiario = rows[i + 1][:-1]
                    break
        elif 'Local de Pagamento' in rows[1]:
            # Subpadrão 6
            for i, row in enumerate(rows):
                if row.startswith('Beneficiário'):
                    row = rows[i + 1]
                    beneficiario = row[:row.find(' - CNPJ:')]
                elif 'Espécie Doc.' in row:
                    num = row[:row.find('Espécie Doc.')].replace('/', '')
                elif '(=) Valor do Documento' in row:
                    valor = rows[i + 1]
                    break
        else:  # subpadrão 3
            valor = None
            for i, row in enumerate(rows):
                if 'Nome do Beneficiário' in row:
                    beneficiario = rows[i + 1]
                    beneficiario = beneficiario[:beneficiario.rfind('.CNPJ')]
                elif '- (-) Descontos/Abatimentos' in row and valor is None:
                    valor = rows[i + 1]
                    break
            for row in rows:
                if 'Espécie DOC' in row:
                    num = row[:row.find('Espécie DOC')]
                    break

        file_name = f'FOLK - {valor} - BOLETO {num} - {beneficiario}.pdf'
        file_name = file_name.replace('/', '')
        return file_name

    def padrao_09(self, rows: List[str]) -> str:
        beneficiario = rows[2][:-15]
        num = rows[3]

        for i, row in enumerate(rows):
            if 'Valor Líquido' in row:
                valor = rows[i + 1]
                break
        file_name = f'FOLK - {valor} - NF{num} - {beneficiario}.pdf'
        return file_name

    def padrao_10(self, rows: List[str]) -> str:
        for i, row in enumerate(rows):
            if '( = ) Valor Cobrado' in row:
                num = rows[i + 1].split()[-1]
                valor = rows[i + 2].split()[1]
            elif 'Agência/Código Beneficiário' in row:
                beneficiario = ' '.join(row.split()[3:])
                break

        file_name = f'FOLK - {valor} - BOLETO - NF{num} - {beneficiario}.pdf'

        return file_name

    def padrao_11(self, rows: List[str]) -> str:
        beneficiario = None
        for i, row in enumerate(rows):
            if 'Espécie Doc' in row:
                num = row[:-11]
            elif 'Beneficiário' in row and beneficiario is None:
                row = rows[i + 1]
                beneficiario = row[:row.find('CPF/CNPJ')]
            elif '(=) Valor do Documento' in row:
                valor = rows[i + 1]
                break

        file_name = f'FOLK - {valor} - BOLETO - {num} - {beneficiario}.pdf'

        return file_name

    def padrao_12(self, rows: List[str]) -> str:
        beneficiario = None
        for i, row in enumerate(rows):
            if 'R$' in row:
                valor = row
            elif 'Beneficiário Final' in row:
                beneficiario = ' '.join(row.split()[2:-2])
            elif 'Espécie Documento' in row:
                num = row[:-17]
                break

        file_name = f'FOLK - {valor} - BOLETO - {num} - {beneficiario}.pdf'

        return file_name

    def padrao_13(self, rows: List[str]) -> str:
        # O modelo 13 (Ligga) tem 3 submodelos.
        if 'CPF/CNPJ' in rows[7]:
            # Modelo 13.1
            for row in rows:
                if 'Descrição dos Produtos' in row:
                    num = row.split()[-4]
                    break
                elif 'R$' in row:
                    valor = row.split()[2]
                    valor = f'R$ {valor[:valor.find(',') + 2]}'
                    beneficiario = ' '.join(row.split()[2:])
                    beneficiario = beneficiario[beneficiario.find(',') + 3:]
            file_name = f'FOLK - {valor} - BOLETO - {num} - {beneficiario}.pdf'
        elif 'Período de Referência' in rows[7]:
            # Modelo 13.2
            for i, row in enumerate(rows[4:], start=4):
                if ',' in row:
                    valor = row.split()[1]
                    valor = f'R$ {valor[:valor.find(',') + 2]}'
                    beneficiario = ' '.join(row.split()[1:])
                    beneficiario = beneficiario[beneficiario.find(',') + 3:]
                    num = rows[i - 1].split()[-1]
                    break
            file_name = f'FOLK - {valor} - BOLETO - {num} - {beneficiario}.pdf'
        else:
            # Modelo 13.3
            for i, row in enumerate(rows):
                if row.startswith('Modelo'):
                    num = row.split()[-1]
                elif 'Tomador dos serviços' in row:
                    beneficiario = rows[i + 1]
                elif 'Valor Total' in row:
                    valor = rows[i + 1].split()[-1]
                    break
            file_name = f'FOLK - R$ {valor} - NF - {num} - {beneficiario}.pdf'

        return file_name

    def padrao_14(self, rows: List[str]) -> str:
        if 'DATA DE RECEBIMENTO' in rows[1] and not rows[1][-1].isnumeric():
            # Subpadrão 3
            for row in rows:
                if 'VALOR TOTAL: ' in row:
                    valor = row.split()[2]
                    beneficiario = ' '.join(row.split()[4: 7])
                    num = row.split()[-1]
                    break
        elif 'DATA DE RECEBIMENTO' in rows[1] and rows[1][-1].isnumeric():
            # Subpadrão 4
            num = ''.join(char for char in rows[1].split()[-1] if char.isnumeric())
            for i, row in enumerate(rows):
                if 'INSCRIÇÃO ESTADUAL UF' in row:
                    beneficiario = ' '.join(rows[i + 4].split()[-4:])
                    valor = rows[i + 11]
                    break
        elif len(rows[1]) > 6:
            # Subpadrão 1
            num = rows[1].split()[-1]
            for i, row in enumerate(rows):
                if row.startswith('MUNICÍPIO'):
                    row = rows[i + 1]
                    row = row[row.rfind('-'):]
                    beneficiario = ' '.join(row.split()[:-1])
                    beneficiario = beneficiario[beneficiario.find('-') + 4:]
                elif row.startswith('FATURA'):
                    valor = rows[i + 1].split()[-1]
                    break
        else:  # Subpadrão 2
            for i, row in enumerate(rows):
                if 'DATA DA EMISSÃO' in row:
                    num = rows[i - 3]
                elif 'FONE/FAX' in row:
                    row = rows[i + 1]
                    beneficiario = ' '.join(row.split()[:3])
                elif row.startswith('BASE DE CÁLCULO DO ICMS'):
                    valor = rows[i + 1].split()[-1]
                    break
        file_name = f'FOLK - {valor} - NF{num} - {beneficiario}.pdf'
        return file_name

    def padrao_15(self, rows: List[str]) -> str:
        beneficiario = None
        for i, row in enumerate(rows):
            if row.startswith('Pagador'):
                row = rows[i + 1]
                beneficiario = row[:row.find('CPF')].strip()
            elif '(=) Valor do Documento' in row:
                valor = rows[i + 1].split()[0][:-3]
            elif 'NUMERO(S) DA(S)' in row:
                num = row.split()[-1].replace('/', '')
                break

        file_name = f'FOLK - {valor} - BOLETO - {num} - {beneficiario}.pdf'

        return file_name

    def padrao_16(self, rows: List[str]) -> str:
        if 'ANS 372609' in rows[0]:
            # Subpadrão 1
            for i, row in enumerate(rows):
                if 'Beneficiário:' in row:
                    beneficiario = ' '.join(row.split()[1:])
                elif '(=) Valor do documento' in row:
                    row = rows[i + 1]
                    valor = row.split()[-2]
                    num = row.split()[-3]
                    break
        elif 'Número do documento CPF/CNPJ' in rows[4]:
            # Subpadrão 2
            for i, row in enumerate(rows):
                if 'Beneﬁciário' in row:
                    row = rows[i + 1]
                    beneficiario = ' '.join(row.split()[:-3])
                    row = rows[i + 3]
                    num = row.split()[0]
                    valor = row.split()[-1]
                    break
        elif 'Agência / Código do Beneficiário' in rows[4]:
            # Subpadrão 3
            for i, row in enumerate(rows):
                if 'Carteira / Nosso númer' in row:
                    row = rows[i + 1]
                    beneficiario = ' '.join(row.split()[:3])
                elif 'Valor documento' in row:
                    num = rows[i + 1]
                    valor = rows[i + 4]
                    break
        elif 'Número do documento CPF/CNPJ' in rows[7]:
            # Subpadrão 4
            for row in rows:
                if 'Beneﬁciário' in row:
                    beneficiario = ' '.join(row.split()[1:])
                    break
            for i, row in enumerate(rows):
                if 'Número do documento CPF/CNPJ' in row:
                    num = rows[i + 1].split()[0]
                    valor = rows[i + 1].split()[-1]
                    break
        elif rows[4].endswith('CNPJ'):
            # Subpadrão 5.
            for i, row in enumerate(rows):
                if 'beneficiário' in row:
                    beneficiario = ' '.join(row.split()[:-2])
                elif 'Nosso número' in row:
                    num = ''.join(char for char in row if char.isnumeric())
                    valor = rows[i + 3]
                    break
        elif rows[4].startswith('Beneficiário'):
            # Subpadrão 6.
            beneficiario = ' '.join(rows[4].split()[1:-1])
            for i, row in enumerate(rows):
                if 'Número do Documento' in row:
                    valor = row[:row.find('Número do Documento')]
                    num = rows[i + 1].split()[0].replace('/', '')
                    break

        file_name = f'FOLK - R$ {valor} - NF - {num} - {beneficiario}.pdf'
        return file_name

    def padrao_17(self, rows: List[str]) -> str:
        for i, row in enumerate(rows):
            if 'Carteira / Nosso númer' in row:
                beneficiario = rows[i + 1]
            elif 'Valor documento' in row:
                num = rows[i + 1]
            elif '(-) Desconto / Abatimentos' in row:
                valor = rows[i - 1]
                break

        file_name = f'FOLK - {valor} - BOLETO - {num} - {beneficiario}.pdf'

        return file_name

    def padrao_18(self, rows: List[str]) -> str:
        num = rows[2].split()[-1]
        valor = rows[3].split()[-1]
        if 'CPF/CNPJ:' in rows[3]:
            beneficiario = ' '.join(rows[3].split()[5:-7])
        else:
            beneficiario = ' '.join(rows[3].split()[7:-5])
        file_name = f'FOLK - {valor} - NF{num} - {beneficiario}.pdf'
        return file_name

    def padrao_19(self, rows: List[str]) -> str:
        for i, row in enumerate(rows):
            if row.startswith('Beneficiário'):
                beneficiario = ' '.join(rows[i + 1].split()[:-2])
            elif 'Espécie Doc.' in row:
                num = ''.join(char for char in row if char.isnumeric())
            elif '(=) Valor do Documento' in row:
                valor = rows[i + 1].strip()
                break

        file_name = f'FOLK - {valor} - BOLETO - {num} - {beneficiario}.pdf'

        return file_name

    def padrao_20(self, rows: List[str]) -> str:
        for i, row in enumerate(rows):
            if 'Data de Emissão' in row:
                num = ''.join(char for char in row if char.isnumeric())
            elif 'Nome/Razão Social' in row:
                beneficiario = ' '.join(row.split()[2:])
        for row in rows:
            if 'Valor dos serviços' in row:
                valor = row.split()[5]
                break
        file_name = f'FOLK - {valor} - NF{num} - {beneficiario}.pdf'
        return file_name

    def padrao_21(self, rows: List[str]) -> str:
        for row in rows:
            if 'Série:' in row:
                num = row[row.find(':') + 1:]
                break
        for i, row in enumerate(rows):
            if '- DESTINATÁRIO:' in row:
                beneficiario = ' '.join(row.split()[5:9])
                valor = rows[i + 1].split()[-1]
                break
        file_name = f'FOLK - {valor} - NF{num} - {beneficiario}.pdf'
        return file_name

    def run(self) -> None:
        # Cria a pasta de destino dos arquivos.
        folder = 'Arquivos'
        if not os.path.exists(folder):
            os.mkdir(folder)
        # Lista todos os códigos de pedido.
        codigos = self.df['ped_codigo'].unique()
        # Percorre todos os códigos.
        for codigo in tqdm(codigos[1830:]):
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
                subfolder = f'{folder}/{codigo}'
                # Cria a pasta para este código.
                if not os.path.exists(subfolder):
                    os.mkdir(subfolder)
                try:
                    file_name = eval(f'self.padrao_{padrao:02}(rows)')
                    file_name = file_name.replace('/', '')
                except (IndexError, UnboundLocalError) as e:
                    print(e)
                    print(padrao)
                    print(path)
                    exit()
                file_name = f'{subfolder}/{file_name}'
                #print(['file_name', file_name])
                try:
                    shutil.copy(path, file_name)
                except FileNotFoundError:
                    # Caso o arquivo não seja encontrado, o nome do diretório será corrigido.
                    try:
                        path = path.replace('Y:\\CELULA FISCAL - FORTES', 'Z:')
                        shutil.copy(path, file_name)
                    except FileNotFoundError:
                        # Caso o arquivo ainda não seja encontrado, será ignorado.
                        pass

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
    '1 /': 9,
    'Pix Copia e Cola': 10,
    'Um banco exclusivo para empresas.': 11,
    'Quem vai receber:': 12,
    'LIGGA TELECOMUNICACOES SA': 13,
    'NF-e': 14,
    'R$': 15,
    'Recibo do Pagador': 16,
    'Instruções de Impressão': 17,
    'DATA DE RECEBIMENTO IDENTIFICAÇÃO E ASSINATURA DO RECEBEDORNF-e': 18
}

#aut = Aut(patterns)
#aut.run()
if __name__ == '__main__':
    try:
        aut = Aut(patterns)
        #aut.run()

        aut.get_example('WERUS METALÚRGICA E MANUTENÇÕES', 5)
        #count = aut.get_count()
        #for key in count:
        #    print(f'{key}: {count[key]}')

    except Exception as e:
        print(e)
        input()

