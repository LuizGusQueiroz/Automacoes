from typing import Dict, List
from tqdm import tqdm
import pandas as pd
import pymssql
import shutil
import os


class Aut:
    def __init__(self, dir_dest: str = 'Arquivos'):
        self.dir_dest = dir_dest
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
            cursor.execute("""
                SELECT
                    CPG.EST_Codigo, 
                    EST.Nome AS EST_Nome,
                    VCP.[Data] AS DT_VENCIMENTO,
                    DPE.[Path] AS CAMINHO_ARQUIVO,
                    VCP.CPG_Codigo AS CODIGO_CONTAS_PAGAR,
                    VCP.Sequencial AS SEQUENCIAL_CONTAS_PAGAR
                FROM PED
                LEFT JOIN DPE
                    ON DPE.EMP_Codigo = PED.EMP_CODIGO AND DPE.PED_Codigo = PED.CODIGO
                LEFT JOIN CPG
                    ON CPG.EMP_Codigo = PED.EMP_CODIGO AND CPG.Codigo = PED.CPG_CODIGO
                LEFT JOIN VCP
                    ON VCP.EMP_Codigo = CPG.EMP_Codigo AND VCP.CPG_Codigo = CPG.Codigo
                LEFT JOIN EST
                    ON EST.EMP_Codigo = CPG.EMP_Codigo AND EST.Codigo = CPG.EST_Codigo
                WHERE CPG.CODIGO IS NOT NULL;
                """)
            """
                Criação de uma lista que irá guardar os resultados da consulta, onde cada item do dicionário será
            um dicionário, com as chaves 'ped_codigo', que é o código do pedido, e 'path' que é o caminho até o arquivo
            referente ao pedido.
            """
            columns = ['EST_Codigo', 'EST_nome', 'dt_vencimento', 'path', 'COD_cpg', 'sequencial']
            df = pd.DataFrame(cursor.fetchall(), columns=columns)
            # Remove valores nulos.
            df.dropna( inplace=True)
            # Corrige a coluna dt_vencimento.
            df['dt_vencimento'] = df['dt_vencimento'].dt.strftime('%d-%m-%Y')
            # Encerrando a conexão
            conn.close()
            cursor.close()

            return df
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def init_dir(self, diretorio: str) -> None:
        """Inicializa o diretório de destino dos arquivos."""
        if not os.path.exists(diretorio):
            os.mkdir(diretorio)

    def run(self) -> None:
        # Cria a pasta de destino dos arquivos.
        self.init_dir(self.dir_dest)
        for _, row in tqdm(self.df.iterrows(), total=len(self.df)):
            path: str = row['path']
            # Verifica se o o arquivo existe.
            if not os.path.exists(path):
                # Caso não existe, o arquivo é procurado no outro servidor.
                path = path.replace('Y:\\CELULA FISCAL - FORTES', 'Z:')
                if not os.path.exists(path):
                    # Caso o arquivo não seja encontrado em nenhum servidor, é ignorado.
                    continue
            estabelecimento: str = row['EST_nome']
            vencimento: str = row['dt_vencimento']
            cod_cpg: str = row['COD_cpg']
            dir_est: str = f'{self.dir_dest}/{estabelecimento}'
            dir_ven: str = f'{dir_est}/{vencimento}'
            # Verifica se já existe a pasta do estabelecimento.
            self.init_dir(dir_est)
            self.init_dir(dir_ven)
            # Define o novo caminho do arquivo.
            nome = path.split('\\')[-1]  # Acessa o nome do arquivo.
            extensao = nome[nome.rfind('.'):]  # Acessa a extensão do arquivo.
            nome = nome[:nome.rfind('.')]  # Remove a extensão do nome do arquivo.
            # Define o nome junto do codigo do CPG, nome antigo e o vencimento.
            novo_nome = f'{cod_cpg} - {nome} - {vencimento}{extensao}'
            new_path = f'{dir_ven}/{novo_nome}'  # Junta o novo nome com o diretório de destino do vencimento.
            try:
                shutil.copy(path, new_path)
            except FileNotFoundError:
                # Pode ocorrer file not found error quando o nome do arquivo é muito grande.
                # Então vai ser tentado apenas diminuir o tamanho do arquivo.
                # O i cria um id para os arquivos, para não haver arquivos de mesmo nome.
                i = len(os.listdir(dir_ven))
                novo_nome = f'{cod_cpg}-{i}-{vencimento}{extensao}'
                try:
                    shutil.copy(path, new_path)
                except FileNotFoundError:
                    # Se o erro persistir, o arquivo será ignorado.
                    print(f'Falha em [{path}].')


if __name__ == '__main__':
    try:
        aut = Aut()
        aut.run()

    except Exception as e:
        print(e)
        input()
