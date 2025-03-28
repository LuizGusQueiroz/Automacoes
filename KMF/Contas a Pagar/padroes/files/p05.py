from PyPDF2 import PdfReader
from typing import List
import os

identificador = 'DANFSe v1.0'


def padrao_05(rows: List[str]) -> str:
    """
    Encontra o nome e o cpf do funionário na lista de linhas da página pdf e retorna um nome de arquivo formatado.
    Args:
        rows (List[str]): Lista de linhas da página do pdf.

    Returns:
        str: O nome formatado para o arquivo. No modelo '{nome}-{cpf}.pdf'.
    """
    
    num_nf = ""
    beneficiario = ""
    valor = ""
    
    for i, row in enumerate(rows):
        if not all([num_nf, beneficiario, valor]):
            # Busca pelo número da Nota Fiscal (NF)
            if 'Número daDPS' in row and not num_nf:
                # Pega a próxima linha (i+1) e filtra apenas os dígitos numéricos
                num_nf_raw = ''.join(filter(str.isdigit, rows[i+1]))
                # Formata o número com 9 dígitos, preenchendo com zeros à esquerda
                num_nf = f"{int(num_nf_raw):09d}"
                # Adiciona pontos separadores a cada 3 dígitos (XXX.XXX.XXX)
                num_nf = f"{num_nf[:3]}.{num_nf[3:6]}.{num_nf[6:]}"
            
            elif 'Nome /Nome Empresarial' in row and not beneficiario:
                beneficiario_line = rows[i+1]
                # Transforma em lista, remove o último elemento e converte de volta para string
                parts = beneficiario_line.split()
                beneficiario = ' '.join(parts[:-1]) if parts else ""
            
            elif 'Valor Líquido daNFS- e' in row and not valor:
                valor_line = rows[i+1]
                # Mantém o valor exatamente como está (com R$ e pontuação original)
                valor = valor_line.strip()
        # Se todos os dados já foram coletados, interrompe o loop
        else:
            break
    
    file_name = f'FOLK - {valor} - NF{num_nf} - {beneficiario}.pdf'
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

# print(os.listdir())

visualizar_texto_pdf('files/padrao_05.pdf')

if __name__ == '__main__':
    file = 'files/padrao_05.pdf'
    with open(file, 'rb') as file_b:
        rows: List[str] = PdfReader(file_b).pages[0].extract_text().split('\n')
        file_name = padrao_05(rows)
    print(file_name)
