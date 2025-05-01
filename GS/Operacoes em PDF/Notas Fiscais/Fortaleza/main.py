import os
from PyPDF2 import PdfReader

def main() -> None:
    files = [file for file in os.listdir() if '.pdf' in file.lower()]

    for file in files:
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b).pages[0]
            rows = pdf.extract_text().split('\n')

        if rows[0] == 'Número da':
            # Modelo 1
            num_nf = rows[1][:4]
            for row in rows:
                if 'Complemento:' in row:
                    nome = row[12:].strip()
                    break
        elif rows[0] == 'Dados do Prestador de Serviços':
            # modelo 2
            primeiro = True
            for i, row in enumerate(rows):
                if row == 'NFS-e':
                    num_nf = rows[i+1]
                if row == 'Razão Social/Nome':
                    if primeiro:
                        primeiro = False
                    else:
                        nome = rows[i+1]
                        break
        elif rows[0] == 'PREFEITURA MUNICIPAL DE FORTALEZA':
            # modelo 3
            for i, row in enumerate(rows):
                if row == 'NFS-e':
                    num_nf = rows[i+1]
                    break
            for row in rows:
                if 'Regime especial Tributação' in row:
                    nome = row[26:]
                    break
        else:
            continue

        os.rename(file, f'NF {num_nf} - {nome}.pdf')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        input()
