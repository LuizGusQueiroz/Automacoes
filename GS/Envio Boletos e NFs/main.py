from PyPDF2 import PdfReader
from typing import List
from tqdm import tqdm
import shutil
import os


class Aut:
    def __init__(self, dir_bol: str, dir_nfs: str, dest: str = 'Arquivos') -> None:
        self.dir_bol = dir_bol  # Diretório dos boletos.
        self.nfs_dir = dir_nfs  # Diretório das notas fiscais.
        self.dest = dest  # Diretório de destino dos arquivos.
        self.dest_bol = f'{dest}/BOLETOS'  # Diretório de destino dos boletos.
        self.dest_nfs = f'{dest}/NOTAS FISCAIS'  # Diretório de destino das notas fiscais.

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

    def processa_boletos(self) -> None:
        # Lista os arquivos do diretório de boletos.
        arquivos: List[str] = os.listdir(self.dir_bol)
        for arquivo in tqdm(arquivos, desc='Processamento Boletos'):
            path = f'{self.dir_bol}/{arquivo}'
            rows: List[str] = self.get_text(path)
            for row in rows:
                if 'CPF/CNPJ:' in row:
                    cnpj = row.split()[-1]
                    cnpj = self.limpa_cnpj(cnpj)
                    break
            else:
                print(f'Arquivo [{arquivo}] falhou.')
                continue
            # Cria a pasta para este CNPJ.
            dest_cnpj: str = f'{self.dest_bol}/{cnpj}'
            self.init_dir(dest_cnpj)
            # Define o novo caminho do arquivo.
            new_path = f'{dest_cnpj}/{arquivo}'
            # Copia o arquivo para a pasta do seu CNPJ.
            shutil.copy(path, new_path)

    def run(self) -> None:
        self.init_dir(self.dest)  # Inicializa o diretório de destino principal.
        self.init_dir(self.dest_bol)  # Inicializa o diretório de destino dos boletos.
        self.init_dir(self.dest_nfs)  # Inicializa o diretório de destino das notas fiscais.

        self.processa_boletos()


if __name__ == "__main__":
    try:
        bol_dir = 'CONDOMINIAIS/BOLETOS'
        nfs_dir = 'CONDOMINIAIS/NOTA FISCAL'
        aut = Aut(bol_dir, nfs_dir)
        aut.run()
    except Exception as e:
        print(e)
        input()