from PyPDF2 import PdfReader
from typing import List
import os


identificador = 'Telefônica Brasil S/A'


def padrao_04(rows: List[str]) -> str:
    """
    Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
    Args:
        rows (List[str]): Lista de linhas da página do pdf.

    Returns:
        str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
    """
    for row in rows:
        if row.startswith('Número da Fatura:'):
            num = row.split()[-1]
        elif 'R$' in row:
            valor = row
            break
    file_name = f'FOLK - {valor} - BOLETO - num{num} - VIVO.pdf'
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
    file = 'files/padrao_04.pdf'
    with open(file, 'rb') as file_b:
        rows: List[str] = PdfReader(file_b).pages[0].extract_text().split('\n')
        file_name = padrao_04(rows)
    print(file_name)
