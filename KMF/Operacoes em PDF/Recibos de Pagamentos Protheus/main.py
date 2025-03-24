import os
from PyPDF2 import PdfReader, PdfWriter
# Função principal que separa os recibos de pagamentos protheus em arquivos menores
# separados pro matrícula e nome
def recibos_de_pagamentos_protheus():
    # Essa função vai separar as páginas pelo nomes no arquivo
    def separar_paginas_por_nome(arquivo_pdf: str, pasta_destino: str) -> int:
        # Verifica o arquivo Pdf existe na pasta
        if not os.path.exists(arquivo_pdf):
            return 0
        # Inicia o processo de separação incluindo todos os arquivos processados em uma pasta 
        os.makedirs(pasta_destino, exist_ok=True)
        num_paginas_processadas = 0

        try:
            with open(arquivo_pdf, 'rb') as file:
                pdf_reader = PdfReader(file)

                for pag_num, pag in enumerate(pdf_reader.pages):
                    texto_pagina = pag.extract_text()

                    if texto_pagina:
                        linhas = texto_pagina.split('\n')
                        matricula = ""
                        nome = ""

                        for linha in linhas:
                            if "Matrícula:" in linha:
                                partes = linha.split("Matrícula:")[1].strip().split("Nome :")
                                if len(partes) == 2:
                                    matricula = partes[0].strip()
                                    nome = partes[1].strip()
                                break

                        if not matricula:
                            for linha in linhas:
                                if "Matrícula" in linha and "Nome" in linha:
                                    partes = linha.replace("Matrícula", "").replace("Nome", "").split(":")
                                    if len(partes) >= 3:
                                        matricula = partes[1].strip()
                                        nome = partes[2].strip()
                                    break

                        if matricula and nome:
                            nome_arquivo = f"{matricula}_{nome}"
                        elif nome:
                            nome_arquivo = f"SemMatricula_{nome}"
                        else:
                            nome_arquivo = f"Pagina_{pag_num+1}"

                        nome_arquivo = "".join(c for c in nome_arquivo if c.isalnum() or c in (' ', '-', '_')).strip()
                        nome_arquivo = nome_arquivo.replace(' ', '_')
                        file_path = os.path.join(pasta_destino, f'{nome_arquivo}.pdf')

                        pdf_writer = PdfWriter()
                        pdf_writer.add_page(pag)

                        with open(file_path, 'wb') as output_pdf:
                            pdf_writer.write(output_pdf)

                        num_paginas_processadas += 1

            return num_paginas_processadas

        except Exception:
            return 0

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
    return total_paginas  # Alteração feita aqui para retornar o total de páginas

if __name__ == "__main__":
    total_processado = recibos_de_pagamentos_protheus()  # Captura o retorno
    print(f"Total de páginas processadas: {total_processado}") 