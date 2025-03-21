from datetime import datetime
from time import sleep
from tqdm import tqdm
from PIL import Image
from sys import exit
import pytesseract
import cv2 as cv
import requests
import shutil
import fitz
import json
import time
import os

# Função Principal para processar os PDFs de Rendimentos DIRF
def rendimento_dirf():
    # Define o diretório onde o script está sendo executado
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))

    # Verifica se o diretório ou arquivo contém "rendimentos dirf"
    if "rendimentos dirf" not in diretorio_atual.lower():
        print("Erro: O diretório ou arquivo não contém 'rendimentos dirf'.")
        return 0

    # Configura o caminho do Tesseract (ajuste conforme necessário)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\user251\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

    # Função para extrair texto de uma imagem usando o Tesseract OCR
    def extract_text(path: str, config='--psm 10') -> str:
        img = cv.imread(path)
        scale_percent = 15  # Aumentar a imagem em 150%
        new_width = int(img.shape[1] * scale_percent)
        new_height = int(img.shape[0] * scale_percent)
        img = cv.resize(img, (new_width, new_height), interpolation=cv.INTER_LANCZOS4)
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(img, config=config)
        return text

    # Função para remover arquivos temporários (imagens) gerados durante o processamento
    def limpa_residuos():
        files = []
        tipos = ['.jpg', '.png']
        for tipo in tipos:
            files += [file for file in os.listdir(diretorio_atual) if tipo in file.lower()]
        for file in files:
            os.remove(os.path.join(diretorio_atual, file))

    # Função para extrair o texto do meio da imagem
    def extrair_texto_do_meio(image_path: str) -> str:
        img = Image.open(image_path)
        width, height = img.size
        meio = img.crop((width * 0.25, height * 0.4, width * 0.75, height * 0.6))  # Área do meio da página
        meio_path = os.path.join(diretorio_atual, 'meio.jpg')
        meio.save(meio_path)
        texto = extract_text(meio_path, config='--psm 6')  # Usar PSM 6 para blocos de texto
        os.remove(meio_path)
        return texto.strip()

    # Função para separar as páginas de um PDF em arquivos diferentes com base no nome e CPF
    def separar_pdf_por_nome_cpf(pdf_path: str, output_dir: str) -> int:
        """Separa as páginas de um PDF em arquivos diferentes com base no nome e CPF.
        Retorna o número de páginas processadas."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        try:
            pdf_document = fitz.open(pdf_path)
        except Exception as e:
            print(f"Erro ao abrir o arquivo {pdf_path}: {e}")
            return 0

        nome_anterior = ""
        cpf_anterior = ""
        novo_documento = None
        paginas_processadas = 0  # Contador de páginas processadas

        for page_num in range(len(pdf_document)):
            try:
                page = pdf_document.load_page(page_num)
                print(f"Processando página {page_num + 1} de {len(pdf_document)} do arquivo {os.path.basename(pdf_path)}")  # Log de progresso

                # Tenta criar o pixmap
                try:
                    image = page.get_pixmap()
                    temp_image_path = os.path.join(diretorio_atual, 'temp_page_image.jpg')
                    image.save(temp_image_path)
                except Exception as e:
                    print(f"Erro ao processar a página {page_num + 1}: {e}")
                    continue  # Pula para a próxima página

                # Extrai o texto do meio da página
                texto_meio = extrair_texto_do_meio(temp_image_path)

                if not texto_meio:
                    # Se não houver texto no meio, junta com a página anterior
                    if novo_documento is not None:
                        novo_documento.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
                else:
                    # Se houver texto no meio, salva a página anterior (se existir) e começa um novo documento
                    if novo_documento is not None:
                        output_path = os.path.join(output_dir, f"{nome_anterior}_{cpf_anterior}.pdf")
                        novo_documento.save(output_path)
                        novo_documento.close()
                        print(f"Arquivo salvo: {output_path}")

                    # Extrai nome e CPF da página atual
                    image = Image.open(temp_image_path)
                    nome = image.crop((150, 185, 550, 198))
                    cpf = image.crop((45, 185, 130, 198))
                    nome_path = os.path.join(diretorio_atual, 'nome.jpg')
                    cpf_path = os.path.join(diretorio_atual, 'cpf.jpg')
                    nome.save(nome_path)
                    cpf.save(cpf_path)

                    nome_completo = extract_text(nome_path, config='--psm 7').strip()
                    cpf_atual = extract_text(cpf_path, config='--psm 13 -c tessedit_char_whitelist=0123456789').strip()

                    nome_anterior = nome_completo
                    cpf_anterior = cpf_atual
                    novo_documento = fitz.open()  # Cria um novo documento PDF
                    novo_documento.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)

                paginas_processadas += 1  # Incrementa o contador de páginas processadas

            except Exception as e:
                print(f"Erro ao processar a página {page_num + 1} do arquivo {pdf_path}: {e}")
            finally:
                # Remove arquivos temporários
                temp_files = ['temp_page_image.jpg', 'nome.jpg', 'cpf.jpg']
                for file in temp_files:
                    file_path = os.path.join(diretorio_atual, file)
                    if os.path.exists(file_path):
                        os.remove(file_path)

        # Salva o último documento criado
        if novo_documento is not None:
            output_path = os.path.join(output_dir, f"{nome_anterior}_{cpf_anterior}.pdf")
            novo_documento.save(output_path)
            novo_documento.close()
            print(f"Arquivo salvo: {output_path}")

        pdf_document.close()
        return paginas_processadas  # Retorna o número de páginas processadas

    # Função para processar todos os PDFs na pasta especificada e separar as páginas com base no nome e CPF
    def processar_todos_pdfs_por_nome_cpf(pasta_pdfs: str, output_dir: str) -> int:
        """Processa todos os PDFs na pasta especificada e separa as páginas com base no nome e CPF.
        Retorna o número total de páginas processadas."""
        if not os.path.exists(pasta_pdfs):
            print(f"Erro: O diretório '{pasta_pdfs}' não existe.")
            exit(1)

        arquivos_pdf = [file for file in os.listdir(pasta_pdfs) if file.lower().endswith('.pdf')]
        print(f"Arquivos PDF encontrados: {arquivos_pdf}")

        total_paginas_processadas = 0  # Contador total de páginas processadas

        for arquivo in tqdm(arquivos_pdf, desc="Processando PDFs", unit="arquivo"):
            pdf_path = os.path.join(pasta_pdfs, arquivo)
            print(f"Processando arquivo: {arquivo}")
            paginas_processadas = separar_pdf_por_nome_cpf(pdf_path, output_dir)
            total_paginas_processadas += paginas_processadas  # Acumula o total de páginas

        return total_paginas_processadas  # Retorna o total de páginas processadas

    # Define a pasta de saída (subpasta "separados" dentro da pasta atual)
    output_dir = os.path.join(diretorio_atual, "separados")

    # Processa todos os PDFs e obtém o número total de páginas processadas
    total_paginas = processar_todos_pdfs_por_nome_cpf(diretorio_atual, output_dir)
    print(f"Total de páginas processadas: {total_paginas}")

if __name__ == "__main__":
    rendimento_dirf()