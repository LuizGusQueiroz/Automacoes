import os
from PyPDF2 import PdfReader

def main() -> None:
    files = [file for file in os.listdir() if '.pdf' in file.lower()]

    for file in files:
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b).pages[0]
            rows = pdf.extract_text().split('\n')

        num_nf = rows[1][:4]
        for row in rows:
            if 'Complemento:' in row:
                nome = row[12:].strip()
                break

        os.rename(file, f'NF {num_nf} - {nome}.pdf')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
