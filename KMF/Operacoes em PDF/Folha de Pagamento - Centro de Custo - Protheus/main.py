from PyPDF2 import PdfReader, PdfWriter
import os
from tqdm import tqdm


def main() -> None:
    centro_custo = ''
    codigo = ''
    novo_centro_custo = '-'
    novo_codigo = '-'
    writer = PdfWriter()
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')

    for file in [file for file in os.listdir() if '.pdf' in file.lower()]:
        with open(file, 'rb') as file:
            pdf = PdfReader(file)
            for page in tqdm(pdf.pages):
                rows = page.extract_text().split('\n')
                for row in rows:
                    if 'C Custo' in row or 'Centro Custo' in row:
                        novo_centro_custo = row.split(': ')[-1].replace('/', '')
                        novo_codigo = row.split(': ')[2][:-9]
                        break
                if novo_centro_custo != centro_custo:
                    if len(writer.pages) > 0:
                        # Salva o atual
                        with open(f'Arquivos/{centro_custo}-{codigo}.pdf', 'wb') as output:
                            writer.write(output)
                    centro_custo = novo_centro_custo
                    codigo = novo_codigo
                    writer = PdfWriter()
                    writer.add_page(page)
                else:
                    writer.add_page(page)
            # Salva o atual
            with open(f'Arquivos/{codigo}-{centro_custo}.pdf', 'wb') as output:
                writer.write(output)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        input()
