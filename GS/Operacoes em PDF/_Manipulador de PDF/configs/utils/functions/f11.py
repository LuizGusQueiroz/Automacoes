from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
import os


def f11() -> int:
    # Cria a pasta de destino dos arquivos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    tot_pags: int = 0
    for arq in [file for file in os.listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            tot_pags += len(pdf_reader.pages)
            # Itera sobre todas as páginas do PDF
            for page in tqdm(pdf_reader.pages):
                rows = page.extract_text().split('\n')

                lotacao = rows[0].replace('.', '').replace('/', '').replace('\\', '')[:-37]

                pdf_writer = PdfWriter()
                # Adiciona a página atual ao objeto PdfWriter
                pdf_writer.add_page(page)
                # Salva a página em um novo arquivo PDF
                with open(f'Arquivos/{lotacao}.pdf', 'wb') as output_file:
                    pdf_writer.write(output_file)
    return tot_pags
