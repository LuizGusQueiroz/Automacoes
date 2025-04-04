from PyPDF2 import PdfReader
from typing import List
import os

identificador = 'Local de pagamento'

def padrao_01(rows: List[str]) -> str:
    """
    Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
    Args:
        rows (List[str]): Lista de linhas da página do pdf.

    Returns:
        str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
    """
    if rows[2].startswith('Pagar preferencialmente'):
        # Subpadrão 1
        for row in rows:
            if 'Nosso número' in row:
                beneficiario = row[row.find('Nosso número')+12:]
            elif 'Espécie documento Aceite' in row:
                num = row[:row.find('Espécie')]
            elif '(=) Valor do documento' in row:
                valor = row[:row.find('(=)')]
                break
    elif rows[2].startswith('Até o vencimento'):
        # Subpadrão 2
        beneficiario = None
        for i, row in enumerate(rows):
            num = ''
            if 'Beneﬁciário' in row and beneficiario is None:
                beneficiario = rows[i+1][:-5]
            elif '(=) Valor do documento' in row:
                valor = rows[i+1]
                break
    file_name = f'FOLK - {valor} - BOLETO - NF{num} - {beneficiario}.pdf'

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
    file = 'files/padrao_01.2.pdf'
    with open(file, 'rb') as file_b:
        rows: List[str] = PdfReader(file_b).pages[0].extract_text().split('\n')
        file_name = padrao_01(rows)
    print(file_name)
