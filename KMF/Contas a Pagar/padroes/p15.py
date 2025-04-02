from PyPDF2 import PdfReader
from typing import List
import os

identificador = 'R$'

def padrao_15(rows: List[str]) -> str:
    """
    Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
    Args:
        rows (List[str]): Lista de linhas da página do pdf.

    Returns:
        str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
    """
    beneficiario = None
    for i, row in enumerate(rows):
        if row.startswith('Pagador'):
            row = rows[i+1]
            beneficiario = row[:row.find('CPF')].strip()
        elif '(=) Valor do Documento' in row:
            valor = rows[i+1].split()[0][:-3]
        elif 'NUMERO(S) DA(S) NOTA(S)' in row:
            num = row.split()[-1].replace('/', '')
            break

    file_name = f'FOLK - {valor} - BOLETO - {num} - {beneficiario}.pdf'

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
    file = 'files/padrao_15.pdf'
    with open(file, 'rb') as file_b:
        rows: List[str] = PdfReader(file_b).pages[0].extract_text().split('\n')
        file_name = padrao_15(rows)
    print(file_name)
