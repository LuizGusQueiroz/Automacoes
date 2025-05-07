from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
import os


def f02() -> int:
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    tot_pags: int = 0
    for arq in [file for file in os.listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf = PdfReader(file)
            tot_pags += len(pdf.pages)
            for pag in tqdm(pdf.pages):
                rows = pag.extract_text().split('\n')
                tipo = rows[0]
                if tipo == 'TERMO DE RESCISÃO DO CONTRATO DE TRABALHO':
                    cpf = rows[40]
                    nome = rows[31]
                elif tipo == 'TERMO DE QUITAÇÃO DE RESCISÃO DO CONTRATO DE TRABALHO':
                    cpf = rows[10][:14]
                    nome = rows[8]
                else:
                    print(f'Tipo de documento não suportado: [{tipo}].')
                    continue

                cpf = ''.join(char for char in cpf if char.isnumeric())
                file_name = f'Arquivos/{nome}{cpf}.pdf'
                writer = PdfWriter()
                if os.path.exists(file_name):
                    pdf_temp = PdfReader(file_name)
                    # Copia todas as páginas do documento do funcionário para o writer
                    for page_num in range(len(pdf_temp.pages)):
                        writer.add_page(pdf_temp.pages[page_num])
                # Adiciona a página atual.
                writer.add_page(pag)
                # Salva o arquivo
                with open(file_name, "wb") as output_pdf:
                    writer.write(output_pdf)
    return tot_pags
