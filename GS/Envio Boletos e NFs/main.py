from PyPDF2 import PdfReader
from typing import List
from tqdm import tqdm
import shutil
import os


class Aut:
    def __init__(self, dir_bol: str, dir_nfs: str, dest: str = 'Arquivos', dir_falhas: str = 'Falhas') -> None:
        self.dir_bol = dir_bol  # Diretório dos boletos.
        self.dir_nfs = dir_nfs  # Diretório das notas fiscais.
        self.dest = dest  # Diretório de destino dos arquivos.
        self.dest_falhas = f'{dest}/{dir_falhas}'  # Diretório de destino de arquivos que falharam.

    def init_dir(self, diretorio: str) -> None:
        """Inicializa o diretório fornecido."""
        if not os.path.exists(diretorio):
            os.mkdir(diretorio)

    def get_text(self, path: str) -> List[str]:
        """
        Acessa o texto do pdf que está no caminho fornecido.
        :param path: Caminho para o pdf.
        """
        if not os.path.exists(path):
            return []
        with open(path, 'rb') as file_bin:
            pdf = PdfReader(file_bin)
            page0 = pdf.pages[0]
            return page0.extract_text().split('\n')

    def limpa_cnpj(self, cnpj: str) -> str:
        """Deixa o cnpj com apenas números."""
        cnpj = ''.join([char for char in cnpj if char.isnumeric()])
        return cnpj

    def processa_arquivos(self, tipo: str) -> None:
        if tipo == 'BOLETOS':
            diretorio = self.dir_bol
        elif tipo == 'NFs':
            diretorio = self.dir_nfs
        else:
            raise TypeError(tipo)

        # Lista os arquivos do diretório de boletos.
        arquivos: List[str] = os.listdir(diretorio)
        for arquivo in tqdm(arquivos, desc=f'Processamento {tipo}'):
            path = f'{diretorio}/{arquivo}'
            rows: List[str] = self.get_text(path)
            for row in rows:
                if tipo == 'BOLETOS' and 'CPF/CNPJ:' in row:
                    cnpj = row.split()[-1]
                    cnpj = self.limpa_cnpj(cnpj)
                    break
                elif tipo == 'NFs' and 'Retenções Federais' in row:
                    cnpj = row[row.find(',') + 3:]
                    cnpj = self.limpa_cnpj(cnpj)
                    break
            else:
                self.init_dir(self.dest_falhas)
                new_path = f'{self.dest_falhas}/{arquivo}'
                shutil.copy(path, new_path)
                continue
            # Cria a pasta para este CNPJ.
            dest_cnpj = f'{self.dest}/{cnpj}'
            self.init_dir(dest_cnpj)
            # Define o novo caminho do arquivo.
            new_path = f'{dest_cnpj}/{arquivo}'
            # Copia o arquivo para a pasta do seu CNPJ.
            shutil.copy(path, new_path)

    def run(self) -> None:
        self.init_dir(self.dest)  # Inicializa o diretório de destino principal.

        self.processa_arquivos('BOLETOS')
        self.processa_arquivos('NFs')


if __name__ == "__main__":
    try:
        bol_dir = 'CONDOMINIAIS/BOLETOS'
        nfs_dir = 'CONDOMINIAIS/NOTA FISCAL'
        aut = Aut(bol_dir, nfs_dir)
        aut.run()
    except Exception as e:
        print(e)
        input()