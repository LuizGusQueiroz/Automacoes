from PyPDF2 import PdfReader
from tqdm import tqdm
import os


def f13() -> int:
    tot_pags: int = 0

    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for file in tqdm(files):
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b).pages[0]
            rows = pdf.extract_text().split('\n')
            tot_pags += len(PdfReader(file_b).pages)
        if rows[0] == 'Número da':
            # Modelo 1
            cnpj = ' ERRO '
            num_nf = ''.join(i for i in rows[1].split()[0] if i.isnumeric())
            for row in rows:
                if 'Complemento:' in row:
                    nome = row[12:].strip()
                    break
        elif rows[0] == 'Dados do Prestador de Serviços':
            # modelo 2
            primeiro = True
            for i, row in enumerate(rows):
                if row == 'NFS-e':
                    num_nf = rows[i + 1]
                if row == 'Razão Social/Nome':
                    if primeiro:
                        primeiro = False
                    else:
                        nome = rows[i + 1]
                        cnpj = ''.join([char for char in rows[i + 3] if char.isnumeric()])
                        break
        else:
            continue
        os.rename(file, f'NF {nome}-{cnpj}.pdf')
    return tot_pags
