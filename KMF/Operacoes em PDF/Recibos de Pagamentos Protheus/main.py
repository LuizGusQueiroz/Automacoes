import os
from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm

def main():
    # Caminho do PDF
    arquivo_pdf = r"C:\Users\user251\Documents\PROJETOS KMF\Automacoes\KMF\Operacoes em PDF\Recibos de Pagamentos Protheus\CONTRACHEQUES-01.2025.pdf"

    # Caminho da pasta de destino
    pasta_destino = r"C:\Users\user251\Documents\PROJETOS KMF\Automacoes\KMF\Operacoes em PDF\Recibos de Pagamentos Protheus\contracheques_separados"
    os.makedirs(pasta_destino, exist_ok=True)

    def separar_paginas_por_nome(arquivo_pdf, pasta_destino):
        arquivos_gerados = []

        with open(arquivo_pdf, 'rb') as file:
            pdf_reader = PdfReader(file)

            for pag_num, pag in enumerate(tqdm(pdf_reader.pages, desc="Processando páginas")):
                texto_pagina = pag.extract_text()

                if texto_pagina:
                    linhas = texto_pagina.split('\n')

                    # Identifica a linha com o nome do empregado
                    for linha in linhas:
                        if "Nome      :" in linha:
                            nome = linha.split("Nome      :")[1].strip()
                            break
                    else:
                        nome = f"Pagina_{pag_num+1}"  # Nome padrão caso não encontre um nome

                    # Limpa caracteres inválidos para nome de arquivo
                    nome_arquivo = ''.join(c for c in nome if c.isalnum() or c in (' ', '-', '_')).strip()
                    file_name = os.path.join(pasta_destino, f'{nome_arquivo}.pdf')

                    # Adiciona a página ao novo arquivo
                    pdf_writer = PdfWriter()
                    pdf_writer.add_page(pag)

                    with open(file_name, 'wb') as output_pdf:
                        pdf_writer.write(output_pdf)

                    arquivos_gerados.append(file_name)

        return arquivos_gerados

    return separar_paginas_por_nome(arquivo_pdf, pasta_destino)

# Executando a função principal
arquivos_criados = main()
