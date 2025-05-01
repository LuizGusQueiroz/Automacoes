from os import listdir, path, mkdir
from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
import pandas as pd
import sys


def get_de_para() -> pd.DataFrame:
    files = [file for file in listdir() if '.xls' in file]
    if len(files) != 1:
        print('Tabela de clientes não encontrada.')
        input()
        sys.exit()
    df = pd.read_excel(files[0])
    df.columns = df.iloc[0]
    return df


def main():
    clientes: pd.DataFrame = get_de_para()

    # Cria a pasta de destino dos recibos
    if not path.exists('Guias'):
        mkdir('Guias')

    for arq in [file for file in listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)

            # Itera sobre todas as páginas do PDF
            for page_pdf in tqdm(pdf_reader.pages):
                page = page_pdf.extract_text().split('\n')

                if 'Tomador: ' in page[10]:
                    cnpj = page[10][page[10].find('Tomador: '):][9:]
                    if cnpj == 'Sem Tomador':
                        continue

                    nome = clientes['Nome'][clientes['Inscrição']==cnpj].values
                    if len(nome) == 1:
                        nome = nome[0].replace('/', '') + '.pdf'
                    else:
                        nome = '_NaoEncontrados.pdf'

                    pdf_writer = PdfWriter()
                    # Adiciona a página atual ao objeto PdfWriter
                    pdf_writer.add_page(page_pdf)

                    # Verifica se o arquivo com este nome já existe, caso exista, junta-o com o novo arquivo
                    if nome in listdir('Guias'):
                        old_pdf = PdfReader(f'Guias/{nome}')
                        for page in old_pdf.pages:
                            pdf_writer.add_page(page)

                    # Salva a página em um novo arquivo PDF
                    with open(f'Guias/{nome}', 'wb') as output_file:
                        pdf_writer.write(output_file)


if __name__ == '__main__':
    main()
