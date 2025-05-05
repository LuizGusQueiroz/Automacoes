import os
import shutil
from typing import List


class Aut:
    def __init__(self, bol_dir: str, nfs_dir: str, dest: str = 'Arquivos') -> None:
        self.bol_dir = bol_dir  # Diretório dos boletos.
        self.nfs_dir = nfs_dir  # Diretório das notas fiscais.
        self.dest = dest  # Diretório de destino dos arquivos.
        self.dest_bol = f'{dest}/BOLETOS'  # Diretório de destino dos boletos.
        self.dest_nfs = f'{dest}/NOTAS FISCAIS'  # Diretório de destino das notas fiscais.

    def init_dir(self) -> None:
        """Inicializa o diretório de destino dos arquivos."""
        if not os.path.exists(self.dest):
            os.mkdir(self.dest)
            os.mkdir(self.dest_bol)
            os.mkdir(self.dest_nfs)

    def processa_boletos(self) -> None:
        # Lista os arquivos do diretório de boletos.
        arquivos: List[str] = os.listdir(self.bol_dir)
        # Padroniza o nome dos arquivos, já que alguns tem '_' no lugar de ' ' entre os itens.
        arquivos_tratados: List[str] = [arquivo.replace('_', ' ') for arquivo in arquivos]
        # Separa as informações de cada arquivo.
        arquivos_tratados: List[List[str]] = [arquivo.split('-') for arquivo in arquivos_tratados]
        # Remove as informações de dia e número de boleto de cada arquivo.
        arquivos_tratados: List[List[str]] = [arquivo[1:-1] for arquivo in arquivos_tratados]
        # Converte cada arquivo que está como lista em string novamente.
        arquivos_tratados: List[str] = [' '.join(arquivo) for arquivo in arquivos_tratados]
        # Remove espaços excedentes no meio dos arquivos.
        arquivos_tratados = [' '.join([nome.strip() for nome in arquivo.split()]) for arquivo in arquivos_tratados]

        # Percorre cada arquivo e nome_tratado ao mesmo tempo.
        for arquivo, nome in zip(arquivos, arquivos_tratados):
            dest_dir: str = f'{self.dest_bol}/{nome}'  # Pasta de destino para o arquivo atual.
            # Verifica se a pasta já existe.
            if not os.path.exists(dest_dir):
                os.mkdir(dest_dir)
            # Adiciona ao nome do arquivo a pasta onde está, para poder ser encontrado.
            old_path = f'{self.bol_dir}/{arquivo}'
            """
            O nome dos arquivos ficam grandes demais, por causa do nome das pastas, gerando erro na hora de mudar,
            por isso, no nome dos arquivos será salvo apenas a data e o número do boleto, sendo estes
            arquivo.split('-')[0:3] e arquivo.split('-')[-1], respectivamente.
            """
            new_path = f'{dest_dir}/{arquivo.split('-')[0]}-{arquivo.split('-')[-1]}'
            # Move o arquivo atual para a sua pasta.
            shutil.copy(old_path, new_path)

    def run(self) -> None:
        self.init_dir()
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
