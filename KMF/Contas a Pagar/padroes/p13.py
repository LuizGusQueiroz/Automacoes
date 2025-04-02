from PyPDF2 import PdfReader
from typing import List
import os

identificador = 'LIGGA TELECOMUNICACOES SA'

def padrao_13(rows: List[str]) -> str:
    """
    Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
    Args:
        rows (List[str]): Lista de linhas da página do pdf.

    Returns:
        str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
    """
    # O modelo 13 (Ligga) tem 3 submodelos.
    if 'CPF/CNPJ' in rows[7]:
        # Modelo 13.1
        for row in rows:
            if 'Descrição dos Produtos' in row:
                num = row.split()[-4]
                break
            elif 'R$' in row:
                valor = row.split()[2]
                valor = f'R$ {valor[:valor.find(',')+2]}'
                beneficiario = ' '.join(row.split()[2:])
                beneficiario = beneficiario[beneficiario.find(',')+3:]
        file_name = f'FOLK - {valor} - BOLETO - {num} - {beneficiario}.pdf'
    elif 'Período de Referência' in rows[7]:
        # Modelo 13.2
        for i, row in enumerate(rows[4:], start=4):
            if ',' in row:
                valor = row.split()[1]
                valor = f'R$ {valor[:valor.find(',') + 2]}'
                beneficiario = ' '.join(row.split()[1:])
                beneficiario = beneficiario[beneficiario.find(',') + 3:]
                num = rows[i-1].split()[-1]
                break
        file_name = f'FOLK - {valor} - BOLETO - {num} - {beneficiario}.pdf'
    else:
        # Modelo 13.3
        for i, row in enumerate(rows):
            if row.startswith('Modelo'):
                num = row.split()[-1]
            elif 'Tomador dos serviços' in row:
                beneficiario = rows[i+1]
            elif 'Valor Total' in row:
                valor = rows[i+1].split()[-1]
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
    file = 'files/padrao_13.3.pdf'
    with open(file, 'rb') as file_b:
        rows: List[str] = PdfReader(file_b).pages[0].extract_text().split('\n')
        file_name = padrao_13(rows)
    print(file_name)
