from PyPDF2 import PdfReader
from typing import List
import os

"""
Exemplo genérico de como deve ser a função para gerar o nome do arquivo para documentos pdf.
"""

# Após a análise do conteúdo do pdf, deve ser guardado uma forma de como identificar este tipo de arquivo,
# pode ser pelo conteúdo de uma das primeiras linhas ou de uma das últimas.
identificador = 'texto inicial'


def padrao_i(rows: List[str], tipo: str) -> str:
    """
    Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
    Args:
        rows (List[str]): Lista de linhas da página do pdf.
        tipo (str): Tipo de agrupamento do arquivo, podendo ser 'sozinho', 'par' ou 'parcelado'. Isto irá afetar a forma
            como o arquivo será renomeado.

    Returns:
        str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
    """
    for row in rows:
        if 'nome' in row:
            nome = row.split()[3]
            break
    cpf = rows[2].split()[5]
    file_name = f'{nome}-{cpf}.pdf'
    if tipo == 'par':
        codigo = rows[1].split()[5]
        file_name = f'{codigo}-{file_name}'
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
    file = ''
    with open(file, 'rb') as file_b:
        rows: List[str] = PdfReader(file_b).pages[0].extract_text().split('\n')
        file_name = padrao_i(rows)
    print(file_name)
