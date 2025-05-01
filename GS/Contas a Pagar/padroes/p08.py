from PyPDF2 import PdfReader
from typing import List
import os


identificador = 'Local de Pagamento'


def padrao_08(rows: List[str]) -> str:
    """
    Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
    Args:
        rows (List[str]): Lista de linhas da página do pdf.

    Returns:
        str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
    """
    if 'Local de Pagamento' in rows[0] and 'Beneficiário' in rows[1]:  # subpadrão 1
        for i, row in enumerate(rows):
            if 'R$' in row:
                row = rows[i+1]
                beneficiario = ' '.join(row.split()[3:])[2:]
                valor = row.split()[2]
                valor = valor[:valor.find(',')+3]
                row = rows[i+2]
                num = row.split()[2]
                num = num[num.find('/')-4:num.find('/')+2]
                break
    elif 'Recibo do Sacado' in rows[0]:
        # subpadrao 2
        for i, row in enumerate(rows):
            if 'Espécie Doc' in row:
                num = row.split()[0]
            elif 'Valor do Documento' in row:
                valor = rows[i+1].strip()
            elif row.startswith('Sacado'):
                beneficiario = ' '.join(row.split()[1:-3])
                break
    elif 'Recibo do Pagador' in rows[0]:
        # subpadrão 4
        beneficiario = None
        for i, row in enumerate(rows):
            if 'Beneficiário' in row and beneficiario is None:
                beneficiario = ' '.join(row.split()[1:-3])
            elif 'Especie Doc.' in row:
                num = row[:row.find('Especie Doc.')]
            elif 'Valor do Documento' in row:
                valor = rows[i+1]
                break
    elif 'Local de Pagamento' in rows[0]:
        # Subpadrão 5
        num = rows[-1]
        for i, row in enumerate(rows):
            if '(=) Valor do documento' in row:
                valor = row.split()[-4][:-2]
            elif '(+) Outros Acréscimos' in row:
                beneficiario = rows[i+1][:-1]
                break
    elif 'Local de Pagamento' in rows[1]:
        # Subpadrão 6
        for i, row in enumerate(rows):
            if row.startswith('Beneficiário'):
                row = rows[i+1]
                beneficiario = row[:row.find(' - CNPJ:')]
            elif 'Espécie Doc.' in row:
                num = row[:row.find('Espécie Doc.')].replace('/', '')
            elif '(=) Valor do Documento' in row:
                valor = rows[i+1]
                break
    else:  # subpadrão 3
        valor = None
        for i, row in enumerate(rows):
            if 'Nome do Beneficiário' in row:
                beneficiario = rows[i+1]
                beneficiario = beneficiario[:beneficiario.rfind('.CNPJ')]
            elif '- (-) Descontos/Abatimentos' in row and valor is None:
                valor = rows[i+1]
                break
        for row in rows:
            if 'Espécie DOC' in row:
                num = row[:row.find('Espécie DOC')]
                break

    file_name = f'FOLK - {valor} - BOLETO {num} - {beneficiario}.pdf'
    file_name = file_name.replace('/', '')
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
    file = 'files/padrao_08.6.pdf'
    with open(file, 'rb') as file_b:
        rows: List[str] = PdfReader(file_b).pages[0].extract_text().split('\n')
        file_name = padrao_08(rows)
    print(file_name)
