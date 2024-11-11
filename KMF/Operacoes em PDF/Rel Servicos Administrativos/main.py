from os import listdir, path, mkdir
from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm


def main():
    # Cria a pasta de destino dos arquivos
    if not path.exists('Arquivos'):
        mkdir('Arquivos')

    for arq in [file for file in listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)

            # Itera sobre todas as páginas do PDF
            for page in tqdm(pdf_reader.pages):
                rows = page.extract_text().split('\n')

                lotacao = rows[0].replace('.', '').replace('/', '').replace('\\', '')[:-37]
                # Remove os zeros à esquerda do código
                try:
                    codigo = int(lotacao.split()[0])
                    lotacao = ' '.join(lotacao.split()[1:])
                except IndexError:
                    continue
                pdf_writer = PdfWriter()
                # Adiciona a página atual ao objeto PdfWriter
                pdf_writer.add_page(page)
                # Salva a página em um novo arquivo PDF
                with open(f'Arquivos/{codigo} {lotacao}.pdf', 'wb') as output_file:
                    pdf_writer.write(output_file)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        input()
