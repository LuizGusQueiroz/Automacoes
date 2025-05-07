from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
import os


def f05() -> int:
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    tot_pags: int = 0

    for file in [file for file in os.listdir() if '.pdf' in file]:
        diretorio = f'Arquivos/{file[:-4]}'
        if not os.path.exists(diretorio):
            os.mkdir(diretorio)
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b)
            tot_pags += len(pdf.pages)
            # Percorre todas as páginas do PDF.
            for page in tqdm(pdf.pages):
                rows = page.extract_text().split('\n')
                for row in rows:
                    if 'Dados Pessoais' in row:
                        nome = row[:-14]
                        break
                writer = PdfWriter()
                writer.add_page(page)
                # Salva a página em um novo arquivo PDF
                with open(f'{diretorio}/{nome}.pdf', 'wb') as output_file:
                    writer.write(output_file)
    return tot_pags
