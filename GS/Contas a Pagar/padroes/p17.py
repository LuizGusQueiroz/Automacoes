from PyPDF2 import PdfReader
from typing import List
import os

identificador = 'Instruções de Impressão'

def padrao_17(rows: List[str]) -> str:
    """
    Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
    Args:
        rows (List[str]): Lista de linhas da página do pdf.

    Returns:
        str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
    """
    for i, row in enumerate(rows):
        if 'Carteira / Nosso númer' in row:
            beneficiario = rows[i+1]
        elif 'Valor documento' in row:
            num = rows[i+1]
        elif '(-) Desconto / Abatimentos' in row:
            valor = rows[i-1]
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
    file = 'files/padrao_17.pdf'
    with open(file, 'rb') as file_b:
        rows: List[str] = PdfReader(file_b).pages[0].extract_text().split('\n')
        file_name = padrao_17(rows)
    print(file_name)
