from PyPDF2 import PdfReader
from typing import List
import os

identificador = 'Recibo do Pagador'
def padrao_16(rows: List[str]) -> str:
    """
    Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
    Args:
        rows (List[str]): Lista de linhas da página do pdf.

    Returns:
        str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
    """
    if 'ANS 372609' in rows[0]:
        # Subpadrão 1
        for i, row in enumerate(rows):
            if 'Beneficiário:' in row:
                beneficiario = ' '.join(row.split()[1:])
            elif '(=) Valor do documento' in row:
                row = rows[i+1]
                valor = row.split()[-2]
                num = row.split()[-3]
                break
    elif 'Número do documento CPF/CNPJ' in rows[4]:
        # Subpadrão 2
        for i, row in enumerate(rows):
            if 'Beneﬁciário' in row:
                row = rows[i+1]
                beneficiario = ' '.join(row.split()[:-3])
                row = rows[i+3]
                num = row.split()[0]
                valor = row.split()[-1]
                break
    elif 'Agência / Código do Beneficiário' in rows[4]:
        # Subpadrão 3
        for i, row in enumerate(rows):
            if 'Carteira / Nosso númer' in row:
                row = rows[i+1]
                beneficiario = ' '.join(row.split()[:3])
            elif 'Valor documento' in row:
                num = rows[i+1]
                valor = rows[i+4]
                break
    elif 'Número do documento CPF/CNPJ' in rows[7]:
        # Subpadrão 4
        for row in rows:
            if 'Beneﬁciário' in row:
                beneficiario = ' '.join(row.split()[1:])
                break
        for i, row in enumerate(rows):
            if 'Número do documento CPF/CNPJ' in row:
                num = rows[i+1].split()[0]
                valor = rows[i+1].split()[-1]
                break
    elif rows[4].endswith('CNPJ'):
        # Subpadrão 5.
        for i, row in enumerate(rows):
            if 'beneficiário' in row:
                beneficiario = ' '.join(row.split()[:-2])
            elif 'Nosso número' in row:
                num = ''.join(char for char in row if char.isnumeric())
                valor = rows[i+3]
                break
    elif rows[4].startswith('Beneficiário'):
        # Subpadrão 6.
        beneficiario = ' '.join(rows[4].split()[1:-1])
        for i, row in enumerate(rows):
            if 'Número do Documento' in row:
                valor = row[:row.find('Número do Documento')]
                num = rows[i+1].split()[0].replace('/', '')
                break

    file_name = f'FOLK - R$ {valor} - NF - {num} - {beneficiario}.pdf'
    return file_name


def visualizar_texto_pdf(file: str) -> None:
    """
    Imprime o texto disponível em um arquivo pdf.
    Args:
        file (str): O caminho para o arquivo pdf.
    """
    with open(file, 'rb') as file_b:
        pdf = PdfReader(file_b)
        page = pdf.pages[0]
        rows = page.extract_text().split('\n')
        for i, row in enumerate(rows):
            print(i, row)


if __name__ == '__main__':
    file = 'files/padrao_16.6.pdf'
    with open(file, 'rb') as file_b:
        rows: List[str] = PdfReader(file_b).pages[0].extract_text().split('\n')
        file_name = padrao_16(rows)
    print(file_name)
