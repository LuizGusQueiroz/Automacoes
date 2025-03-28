import os
from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
import pandas as pd
import sys

# Esta função tem como objetivo carregar e preparar uma tabela de dados (DataFrame) 
# a partir de um arquivo Excel que contém informações de clientes
def get_de_para() -> pd.DataFrame:
    files = [file for file in os.listdir() if '.xls' in file]
    if len(files) != 1:
        print('Tabela de clientes não encontrada.')
        input()
        sys.exit()
    df = pd.read_excel(files[0])
    df.columns = df.iloc[0]
    return df
    
# Remove '.', '/', '-' dos cnpj do tomador
def clean_cnpj(cnpj: str) -> str:
    """Remove apenas '.', '/' e '-' do CNPJ"""
    return cnpj.replace('.', '').replace('/', '').replace('-', '')

# Remove os caracteres especiais quando for salvar as pastas
def safe_folder_name(name: str) -> str:
    """Remove caracteres inválidos para nomes de pasta"""
    invalid_chars = '<>:"/\\'
    for char in invalid_chars:
        name = name.replace(char, '')
    return name.strip()

# Função principal do código
def re_fgts_por_empresa():
    clientes: pd.DataFrame = get_de_para()
    total_paginas = 0
    for arq in [file for file in os.listdir() if file.lower().endswith('.pdf')]:
        with open(arq, 'rb') as file:
            pdf_reader = PdfReader(file)
            total_paginas += len(pdf_reader.pages)
            # Processa cada página individualmente
            for page_pdf in tqdm(pdf_reader.pages, desc=f"Processando {arq}"):
                page = page_pdf.extract_text().split('\n')
                
                # Extrai nome do empregador
                if 'Nome Empregador' in page[1]:
                    empregador = page[1][page[1].rfind('Empregador: '):][12:].strip()
                
                # Cria pasta para o empregador
                pasta_empregador = safe_folder_name(empregador)
                if not os.path.exists(pasta_empregador):
                    os.mkdir(pasta_empregador)
                
                # Processa tomadores
                if 'Tomador: ' in page[10]:
                    cnpj = page[10][page[10].find('Tomador: ')+9:].strip()
                    if cnpj == 'Sem Tomador':
                        continue
                    
                    # Busca na tabela com CNPJ original
                    nome = clientes['Nome'][clientes['Inscrição'] == cnpj].values
                    cnpj_limpo = clean_cnpj(cnpj)
                    
                    if len(nome) == 1:
                        nome_arquivo = f"{safe_folder_name(nome[0])}_{cnpj_limpo}.pdf"
                    else:
                        nome_arquivo = f"{cnpj_limpo}_NaoEncontrado.pdf"
                    
                    pdf_writer = PdfWriter()
                    pdf_writer.add_page(page_pdf)

                    # Caminho completo do arquivo
                    output_path = os.path.join(pasta_empregador, nome_arquivo)
                    
                    # Verifica se arquivo já existe para mesclar
                    if os.path.exists(output_path):
                        old_pdf = PdfReader(output_path)
                        for old_page in old_pdf.pages:
                            pdf_writer.add_page(old_page)

                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)
    return total_paginas                    
    
   
if __name__ == '__main__':
    re_fgts_por_empresa()
    x = re_fgts_por_empresa()
    print(x)