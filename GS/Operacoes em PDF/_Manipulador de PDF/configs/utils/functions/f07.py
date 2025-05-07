from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
import pandas as pd
import os


def f07() -> int:  # 7
    def get_de_para() -> pd.DataFrame | None:
        files = [file for file in os.listdir() if '.xls' in file]
        if len(files) == 0:
            return None
        df = pd.read_excel(files[0])
        df.columns = df.iloc[0]
        return df

    clientes: pd.DataFrame | None = get_de_para()
    tem_excel: bool = clientes is not None
    # Cria a pasta de destino dos recibos
    if not os.path.exists('Arquivos do fgts'):
        os.mkdir('Arquivos do fgts')
    tot_pags: int = 0

    for arq in [file for file in os.listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            tot_pags += len(pdf_reader.pages)
            # Itera sobre todas as páginas do PDF
            for page_pdf in tqdm(pdf_reader.pages):
                page = page_pdf.extract_text().split('\n')

                if tem_excel:
                    if 'Tomador: ' in page[10]:
                        cnpj = page[10][page[10].find('Tomador: '):][9:]
                        if cnpj == 'Sem Tomador':
                            continue

                        nome = clientes['Nome'][clientes['Inscrição'] == cnpj].values
                        if len(nome) == 1:
                            nome = nome[0].replace('/', '') + '.pdf'
                        else:
                            nome = '_NaoEncontrados.pdf'

                        pdf_writer = PdfWriter()
                        # Adiciona a página atual ao objeto PdfWriter
                        pdf_writer.add_page(page_pdf)

                        # Verifica se o arquivo com este nome já existe, caso exista, junta-o com o novo arquivo
                        if nome in os.listdir('Arquivos do fgts'):
                            old_pdf = PdfReader(f'Arquivos do fgts/{nome}')
                            for page in old_pdf.pages:
                                pdf_writer.add_page(page)

                        # Salva a página em um novo arquivo PDF
                        with open(f'Arquivos do fgts/{nome}', 'wb') as output_file:
                            pdf_writer.write(output_file)
                else:
                    for row in page:
                        if 'Tomador: ' in row:
                            cnpj = row[row.find('Tomador: ') + 9:]
                            nome = f'{cnpj.replace('/', '').replace('-', '').replace('.', '')}.pdf'
                            break
                    pdf_writer = PdfWriter()
                    # Adiciona a página atual ao objeto PdfWriter
                    pdf_writer.add_page(page_pdf)

                    # Verifica se o arquivo com este nome já existe, caso exista, junta-o com o novo arquivo
                    if nome in os.listdir('Arquivos do fgts'):
                        old_pdf = PdfReader(f'Arquivos do fgts/{nome}')
                        for page in old_pdf.pages:
                            pdf_writer.add_page(page)

                    # Salva a página em um novo arquivo PDF
                    with open(f'Arquivos do fgts/{nome}', 'wb') as output_file:
                        pdf_writer.write(output_file)
    return tot_pags
