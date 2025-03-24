import os
from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
# Função principal que contém todas as outras funções e processa os PDFs
def recibos_de_pagamentos_protheus():
   
    def separar_paginas_por_nome(arquivo_pdf: str, pasta_destino: str) -> int:
        
        # Verifica se o arquivo existe
        if not os.path.exists(arquivo_pdf):
            print(f"Arquivo não encontrado: {arquivo_pdf}")
            return 0
        
        # Cria a pasta de destino se ela não existir
        os.makedirs(pasta_destino, exist_ok=True)

        # Contador de páginas processadas
        num_paginas_processadas = 0

        try:
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

                        num_paginas_processadas += 1

            return num_paginas_processadas

        except (FileNotFoundError, PdfReadError) as e:
            print(f"Erro ao processar o arquivo {arquivo_pdf}: {e}")
            return 0

    def processar_pdfs_na_pasta(pasta_pdf: str, pasta_destino: str) -> int:
        """
        Processa todos os PDFs na pasta especificada e separa as páginas com base no nome.
        Retorna o número total de páginas processadas.
        """
        # Verifica se a pasta existe
        if not os.path.exists(pasta_pdf):
            print(f"Pasta não encontrada: {pasta_pdf}")
            return 0

        # Lista todos os arquivos PDF na pasta
        arquivos_pdf = [arquivo for arquivo in os.listdir(pasta_pdf) if arquivo.lower().endswith('.pdf')]

        # Contador total de páginas processadas
        total_paginas_processadas = 0

        # Processa cada arquivo PDF
        for arquivo in arquivos_pdf:
            caminho_arquivo = os.path.join(pasta_pdf, arquivo)
            print(f"Processando arquivo: {arquivo}")
            paginas_processadas = separar_paginas_por_nome(caminho_arquivo, pasta_destino)
            total_paginas_processadas += paginas_processadas

        return total_paginas_processadas

    # Obtém o diretório atual do script
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))

    # Define a pasta de destino (subpasta "separados" dentro da pasta atual)
    pasta_destino = os.path.join(diretorio_atual, "separados")

    # Processa todos os PDFs na pasta atual
    total_paginas = processar_pdfs_na_pasta(diretorio_atual, pasta_destino)
    print(f"Total de páginas processadas: {total_paginas}")

# Executa a função principal
if __name__ == "__main__":
    recibos_de_pagamentos_protheus()