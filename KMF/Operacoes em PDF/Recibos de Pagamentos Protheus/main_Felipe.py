import os
from PyPDF2 import PdfReader, PdfWriter
import re

def recibos_de_pagamentos_protheus():
    def separar_paginas_por_nome(arquivo_pdf: str, pasta_destino: str) -> int:
        if not os.path.exists(arquivo_pdf):
            return 0

        os.makedirs(pasta_destino, exist_ok=True)
        num_paginas_processadas = 0

        with open(arquivo_pdf, 'rb') as file:
            pdf_reader = PdfReader(file)

            for pag_num, pag in enumerate(pdf_reader.pages):
                texto_pagina = pag.extract_text()

                if not texto_pagina:
                    continue

                linhas = texto_pagina.split('\n')
                matricula = ""
                nome = ""

                # Expressão regular ajustada para capturar apenas a matrícula e o nome
                for linha in linhas:
                    match = re.search(r'Matrícula\s*:\s*(\d+)\s+Nome\s*:\s*([A-ZÀ-Ú ]+)', linha)
                    if match:
                        matricula = match.group(1)
                        nome = match.group(2).strip()
                        # Garante que o nome não tenha palavras extras como "Local"
                        nome = re.sub(r'\s+L$', '', nome)  # Remove um "L" no final caso tenha vindo junto
                        break  # Encontrou, pode sair do loop

                # Formatação do nome do arquivo
                if matricula and nome:
                    nome_arquivo = f"{matricula}_{nome}"
                elif nome:
                    nome_arquivo = f"SemMatricula_{nome}"
                else:
                    nome_arquivo = f"Pagina_{pag_num+1}"

                # Limpeza do nome do arquivo
                nome_arquivo = re.sub(r'[^A-Za-z0-9À-Ú_]', '', nome_arquivo)  # Remove caracteres inválidos
                nome_arquivo = nome_arquivo.rstrip('_')  # Remove underlines finais extras

                file_path = os.path.join(pasta_destino, f'{nome_arquivo}.pdf')

                pdf_writer = PdfWriter()
                pdf_writer.add_page(pag)

                with open(file_path, 'wb') as output_pdf:
                    pdf_writer.write(output_pdf)

                num_paginas_processadas += 1

        return num_paginas_processadas
    # Essa função percorre todos os PDFs dentro de uma pasta e processa um por um
    def processar_pdfs_na_pasta(pasta_pdf: str, pasta_destino: str) -> int:
        if not os.path.exists(pasta_pdf):
            return 0

        arquivos_pdf = [arquivo for arquivo in os.listdir(pasta_pdf) if arquivo.lower().endswith('.pdf')]
        total_paginas_processadas = 0

        for arquivo in arquivos_pdf:
            caminho_arquivo = os.path.join(pasta_pdf, arquivo)
            paginas_processadas = separar_paginas_por_nome(caminho_arquivo, pasta_destino)
            total_paginas_processadas += paginas_processadas

        return total_paginas_processadas

    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    pasta_destino = os.path.join(diretorio_atual, "separados")

    total_paginas = processar_pdfs_na_pasta(diretorio_atual, pasta_destino)
    return total_paginas

if __name__ == "__main__":
    recibos_de_pagamentos_protheus()
