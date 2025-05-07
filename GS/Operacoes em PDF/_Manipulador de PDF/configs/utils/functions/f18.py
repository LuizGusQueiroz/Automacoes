from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
import os


def f18() -> int:
    tot_pags = 0
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    writer = PdfWriter()
    cpf = ''
    nome = ''
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for file in files:
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b)
            tot_pags += len(pdf.pages)
            for page in tqdm(pdf.pages):
                rows = page.extract_text().split('\n')
                if rows[0] == 'MINISTÉRIO DA FAZENDA':
                    # MINISTÉRIO DA FAZENDA indica o começo de um novo funcionário, então o
                    # conteúdo atual é salvo, se existir.
                    if len(writer.pages):
                        file_name = f'Arquivos/{nome}-{cpf}-{cnpj}.pdf'
                        with open(file_name, 'wb') as output:
                            writer.write(output)
                        # Inicia um novo writer
                        writer = PdfWriter()
                    writer.add_page(page)
                    # Guarda o CNPJ da empresa.
                    cnpj = ''.join(char for char in rows[7] if char.isnumeric())
                    # Procura o nome e CPF no novo documento.
                    for i, row in enumerate(rows):
                        achou = False
                        if 'Título de Eleitor' in row:
                            achou = True
                            cpf = ''.join(char for char in row if char.isnumeric())
                            nome = rows[i+2]
                            for char in ['|', '/', '\\']:
                                nome = nome.replace(char, '')
                            break
                    if not achou:
                        raise Exception(f'Nome e CPF não encontrados: {file}')
                else:
                    writer.add_page(page)
            # Salva o último aberto
            file_name = f'Arquivos/{nome}-{cpf}.pdf'
            with open(file_name, 'wb') as output:
                writer.write(output)

    return tot_pags
