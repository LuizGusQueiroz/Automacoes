from PyPDF2 import PdfReader, PdfWriter
from os import listdir, mkdir, path
from tqdm import tqdm


def main():
    if not path.exists('Arquivos'):
        mkdir('Arquivos')

    for file in [file for file in listdir() if '.pdf' in file]:
        diretorio = f'Arquivos/{file[:-4]}'
        if not path.exists(diretorio):
            mkdir(diretorio)

        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b)

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


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
