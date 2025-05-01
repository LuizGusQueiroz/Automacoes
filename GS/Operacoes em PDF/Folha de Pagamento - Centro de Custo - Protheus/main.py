from PyPDF2 import PdfReader, PdfWriter
import os
from tqdm import tqdm
import pandas as pd


def get_tabela() -> pd.DataFrame:
    files = [file for file in os.listdir() if '.xls' in file]
    if len(files) != 1:
        return pd.DataFrame()
    return pd.read_excel(files[0], header=2)

def main() -> int:
    tot_pags = 0
    df = get_tabela()
    tem_relacao = len(df) > 0
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
            tot_pags += len(pdf.pages)
            for page in tqdm(pdf.pages):
                rows = page.extract_text().split('\n')
                for row in rows:
                    if 'C Custo' in row or 'Centro Custo' in row:
                        novo_centro_custo = row.split(': ')[-1].replace('/', '')
                        novo_codigo = row.split(': ')[2][:-9]
                        break
                if novo_centro_custo != centro_custo:
                    if len(writer.pages) > 0:
                        cnpj = ''
                        if tem_relacao:
                            result = df[df['Desc Moeda 1'] == centro_custo]['CNPJ/CEI Tom'].tolist()
                            if len(result) == 1:
                                cnpj = ''.join(char for char in str(result[0]) if char.isnumeric())
                        # Salva o atual
                        with open(f'Arquivos/{codigo}-{centro_custo}-{cnpj}.pdf', 'wb') as output:
                            writer.write(output)
                    centro_custo = novo_centro_custo
                    codigo = novo_codigo
                    writer = PdfWriter()
                    writer.add_page(page)
                else:
                    writer.add_page(page)
            cnpj = ''
            if tem_relacao:
                result = df[df['Desc Moeda 1']==centro_custo]['CNPJ/CEI Tom'].tolist()
                if len(result) == 1:
                    cnpj = ''.join(char for char in result[0] if char.isnumeric())
                    print(cnpj)
            # Salva o atual
            with open(f'Arquivos/{codigo}-{centro_custo}-{cnpj}.pdf', 'wb') as output:
                writer.write(output)
    return tot_pags


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        input()
