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
    for row in rows:
        if 'Nosso número' in row:
            beneficiario = row[row.find('Nosso número')+12:]
        elif 'Espécie documento Aceite' in row:
            num_nf = row[:row.find('Espécie')]
        elif '(=) Valor do documento' in row:
            valor = row[:row.find('(=)')]
            break
    file_name = f'FOLK - {valor} - BOLETO - NF{num_nf} - {beneficiario}.pdf'

    return file_name


if __name__ == '__main__':
    file = 'files/padrao_01.pdf'
    with open(file, 'rb') as file_b:
        rows: List[str] = PdfReader(file_b).pages[0].extract_text().split('\n')
        file_name = padrao_01(rows)
    print(file_name)
