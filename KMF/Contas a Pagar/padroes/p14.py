from PyPDF2 import PdfReader
from typing import List
import os


identificador = 'NF-e'

def padrao_14(rows: List[str]) -> str:
    """
    Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
    Args:
        rows (List[str]): Lista de linhas da página do pdf.

    Returns:
        str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
    """
    if 'DATA DE RECEBIMENTO' in rows[1] and not rows[1][-1].isnumeric():
        # Subpadrão 3
        for row in rows:
            if 'VALOR TOTAL: ' in row:
                valor = row.split()[2]
                beneficiario = ' '.join(row.split()[4: 7])
                num = row.split()[-1]
                break
    elif 'DATA DE RECEBIMENTO' in rows[1] and rows[1][-1].isnumeric():
        # Subpadrão 4
        num = ''.join(char for char in rows[1].split()[-1] if char.isnumeric())
        for i, row in enumerate(rows):
            if 'INSCRIÇÃO ESTADUAL UF' in row:
                beneficiario =  ' '.join(rows[i+4].split()[-4:])
                valor = rows[i+11]
                break
    elif len(rows[1]) > 6:
        # Subpadrão 1
        num = rows[1].split()[-1]
        for i, row in enumerate(rows):
            if row.startswith('MUNICÍPIO'):
                row = rows[i+1]
                row = row[row.rfind('-'):]
                beneficiario = ' '.join(row.split()[:-1])
                beneficiario = beneficiario[beneficiario.find('-')+4:]
            elif row.startswith('FATURA'):
                valor = rows[i+1].split()[-1]
                break
    else:  # Subpadrão 2
        for i, row in enumerate(rows):
            if 'DATA DA EMISSÃO' in row:
                num = rows[i-3]
            elif 'FONE/FAX' in row:
                row = rows[i+1]
                beneficiario = ' '.join(row.split()[:3])
            elif row.startswith('BASE DE CÁLCULO DO ICMS'):
                valor = rows[i+1].split()[-1]
                break
    file_name = f'FOLK - {valor} - NF{num} - {beneficiario}.pdf'
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
    file = 'files/padrao_14.4.pdf'
    with open(file, 'rb') as file_b:
        rows: List[str] = PdfReader(file_b).pages[0].extract_text().split('\n')
        file_name = padrao_14(rows)
    print(file_name)
