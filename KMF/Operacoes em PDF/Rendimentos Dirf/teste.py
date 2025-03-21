from datetime import datetime
from typing import List, Dict
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

# Define o diretório onde os PDFs estão armazenados
diretorio_pdf = r"C:\Users\user251\Documents\PROJETOS KMF\Automacoes\KMF\Operacoes em PDF\Rendimentos Dirf"

# Altera o diretório de trabalho para o local dos PDFs
os.chdir(diretorio_pdf)

# Configura o caminho do Tesseract (ajuste conforme necessário)
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\user251\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def extract_text(path: str, config='--psm 10') -> str:
    """Extrai texto de uma imagem usando o Tesseract OCR."""
    img = cv.imread(path)
    scale_percent = 15  # Aumentar a imagem em 150%
    new_width = int(img.shape[1] * scale_percent)
    new_height = int(img.shape[0] * scale_percent)
    img = cv.resize(img, (new_width, new_height), interpolation=cv.INTER_LANCZOS4)
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(img, config=config)
    return text

def limpa_residuos():
    """Remove arquivos temporários (imagens) gerados durante o processamento."""
    files = []
    tipos = ['.jpg', '.png']
    for tipo in tipos:
        files += [file for file in os.listdir() if tipo in file.lower()]
    for file in files:
        os.remove(file)

def extrair_texto_do_meio(image_path: str) -> str:
    """Extrai o texto do meio da imagem."""
    img = Image.open(image_path)
    width, height = img.size
    meio = img.crop((width * 0.25, height * 0.4, width * 0.75, height * 0.6))  # Área do meio da página
    meio.save('meio.jpg')
    texto = extract_text('meio.jpg', config='--psm 6')  # Usar PSM 6 para blocos de texto
    os.remove('meio.jpg')
    return texto.strip()

def separar_pdf_por_nome_cpf(pdf_path: str, output_dir: str):
    """Separa as páginas de um PDF em arquivos diferentes com base no nome e CPF."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        pdf_document = fitz.open(pdf_path)
    except Exception as e:
        print(f"Erro ao abrir o arquivo {pdf_path}: {e}")
        return

    nome_anterior = ""
    cpf_anterior = ""
    novo_documento = None

    for page_num in range(len(pdf_document)):
        try:
            page = pdf_document.load_page(page_num)
            print(f"Processando página {page_num + 1} de {len(pdf_document)}")  # Log de progresso

            # Tenta criar o pixmap
            try:
                image = page.get_pixmap()
                image.save('temp_page_image.jpg')
            except Exception as e:
                print(f"Erro ao processar a página {page_num + 1}: {e}")
                continue  # Pula para a próxima página

            # Extrai o texto do meio da página
            texto_meio = extrair_texto_do_meio('temp_page_image.jpg')

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
                image = Image.open('temp_page_image.jpg')
                nome = image.crop((150, 185, 550, 198))
                cpf = image.crop((45, 185, 130, 198))
                nome.save('nome.jpg')
                cpf.save('cpf.jpg')

                nome_completo = extract_text('nome.jpg', config='--psm 7').strip()
                cpf_atual = extract_text('cpf.jpg', config='--psm 13 -c tessedit_char_whitelist=0123456789').strip()

                nome_anterior = nome_completo
                cpf_anterior = cpf_atual
                novo_documento = fitz.open()  # Cria um novo documento PDF
                novo_documento.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)

        except Exception as e:
            print(f"Erro ao processar a página {page_num + 1} do arquivo {pdf_path}: {e}")
        finally:
            # Remove arquivos temporários
            if os.path.exists('temp_page_image.jpg'):
                os.remove('temp_page_image.jpg')
            if os.path.exists('nome.jpg'):
                os.remove('nome.jpg')
            if os.path.exists('cpf.jpg'):
                os.remove('cpf.jpg')

    # Salva o último documento criado
    if novo_documento is not None:
        output_path = os.path.join(output_dir, f"{nome_anterior}_{cpf_anterior}.pdf")
        novo_documento.save(output_path)
        novo_documento.close()
        print(f"Arquivo salvo: {output_path}")

    pdf_document.close()

def processar_todos_pdfs_por_nome_cpf(pasta_pdfs: str, output_dir: str):
    """Processa todos os PDFs na pasta especificada e separa as páginas com base no nome e CPF."""
    if not os.path.exists(pasta_pdfs):
        print(f"Erro: O diretório '{pasta_pdfs}' não existe.")
        exit(1)

    arquivos_pdf = [file for file in os.listdir(pasta_pdfs) if file.lower().endswith('.pdf')]
    print(f"Arquivos PDF encontrados: {arquivos_pdf}")

    for arquivo in tqdm(arquivos_pdf, desc="Processando PDFs", unit="arquivo"):
        pdf_path = os.path.join(pasta_pdfs, arquivo)
        print(f"Processando: {pdf_path}")
        separar_pdf_por_nome_cpf(pdf_path, output_dir)

def main():
    """Função principal para processar os PDFs."""
    # Define a pasta de saída (subpasta "separados" dentro da pasta de PDFs)
    output_dir = os.path.join(diretorio_pdf, "separados")

    # Processa todos os PDFs
    processar_todos_pdfs_por_nome_cpf(diretorio_pdf, output_dir)

if __name__ == "__main__":
    main()


