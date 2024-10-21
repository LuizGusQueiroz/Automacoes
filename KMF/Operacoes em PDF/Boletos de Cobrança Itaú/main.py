from os import listdir, path, mkdir
from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm


def main():
    # Cria a pasta de destino dos recibos
    if not path.exists('Boletos'):
        mkdir('Boletos')

    for arq in [file for file in listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)

            # Itera sobre todas as páginas do PDF
            for page_pdf in tqdm(pdf_reader.pages):
                page = page_pdf.extract_text().split('\n')

                for row in page:
                    if 'UF: Agente:CEP:Data Vencimento:' in row:
                        condominio = row[row.rfind(':')+1:]
                        break
                for row in page:
                    if 'Data Impressão:' in row:
                        numero = row.split()[-1].replace('/', '')
                        break

                nome_arq = f'{condominio}-{numero}.pdf'
                pdf_writer = PdfWriter()
                # Adiciona a página atual ao objeto PdfWriter
                pdf_writer.add_page(page_pdf)
                # Salva a página em um novo arquivo PDF
                with open(f'Boletos\\{nome_arq}', 'wb') as output_file:
                    pdf_writer.write(output_file)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
