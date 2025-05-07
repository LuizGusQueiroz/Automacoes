from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
import os


def f12() -> int:  # 12
    # Cria a pasta de destino dos recibos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    tot_pags: int = 0
    for arq in [file for file in os.listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            pdf_writer = PdfWriter()
            empresa = ''
            tot_pags += len(pdf_reader.pages)
            for page_pdf in tqdm(pdf_reader.pages):
                page = page_pdf.extract_text().split('\n')
                # Acessa o nome e CNPJ da empresa
                for row in page:
                    if 'Empresa: ' in row:
                        idx = 1
                        while not row[-idx].isnumeric():
                            idx += 1
                        row = row[8:1 - idx].split()
                        cnpj = ''.join(i for i in row[-1] if i.isnumeric())
                        idx = 0
                        while row[idx] != '-':
                            idx += 1
                        empresa_nova = ' '.join(row[:idx])
                        break

                # Verifica se a empresa e a mesma, se for, junta as páginas,
                # caso contrário, salva o arquivo atual e cria um pdf novo.
                if empresa_nova != empresa:
                    if pdf_writer.pages:
                        with open(f'Arquivos/{empresa}-{cnpj}.pdf', 'wb') as output_file:
                            pdf_writer.write(output_file)
                        pdf_writer = PdfWriter()
                    empresa = empresa_nova
                    pdf_writer.add_page(page_pdf)
                else:
                    pdf_writer.add_page(page_pdf)
            # Salva o último arquivo aberto
            with open(f'Arquivos/{empresa}-{cnpj}.pdf', 'wb') as output_file:
                pdf_writer.write(output_file)
            pdf_writer = PdfWriter()
    return tot_pags
