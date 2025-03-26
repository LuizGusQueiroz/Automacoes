from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PyPDF2 import PdfReader, PdfWriter
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
import re

pytesseract.pytesseract.tesseract_cmd = f'{os.getcwd()}/../_Manipulador de PDF - Tess/configs/tess/tesseract.exe'

# Coordenadas do local do nome do cliente e número da nota para cada dimensão de cada prefeitura.
all_sizes = {'Curitiba':   {(612, 792): [(125, 240, 350, 255), (505,  52, 535,  63)],
                            (595, 842): [(110, 235, 380, 255), (520,  30, 550,  45)]},
             'Salvador':   {(595, 842): [( 10, 198, 250, 208), (445,  22, 500,  32)]},
             'Sorocaba':   {(595, 842): [(135, 300, 370, 310), (260, 108, 276, 116)]},
             'Vitória':    {(596, 842): [(110, 255, 400, 270), (405,  38, 450,  50)]}}



def extract_text(path: str, config='--psm 10') -> str:
    img = cv.imread(path)
    scale_percent = 15  # Aumentar a imagem em 150%
    # Calculando o novo tamanho
    new_width = int(img.shape[1] * scale_percent)
    new_height = int(img.shape[0] * scale_percent)
    # Redimensionar a imagem proporcionalmente
    img = cv.resize(img, (new_width, new_height), interpolation=cv.INTER_LANCZOS4)
    # 1. Conversão para escala de cinza
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Executar o OCR na imagem processada
    text = pytesseract.image_to_string(img, config=config)
    return text


def pdf_split(path: str) -> None:
    with open(path, 'rb') as file:
        pdf = PdfReader(file)
        if len(pdf.pages) > 1:
            for i, page in enumerate(pdf.pages):
                writer = PdfWriter()
                writer.add_page(page)
                with open(f'{path[:-4]}-{i}.pdf', 'wb') as output:
                    writer.write(output)


def pdf_to_img(path: str, sizes: Dict, page: int = 0) -> None:
    pdf_document = fitz.open(path)  # Abre a Nota Fiscal.
    page = pdf_document.load_page(page)  # Carrega a página.
    image = page.get_pixmap()  # Converte a página num objeto de imagem.
    image.save('img.jpg')  # Salva a imagem num arquivo.
    pdf_document.close()  # Fechar o PDF para garantir que o arquivo seja liberado
    image = Image.open('img.jpg')
    if image.size in sizes:
        nome = image.crop(sizes[image.size][0])
        num_nf = image.crop(sizes[image.size][1])
    else:
        raise TypeError()
    nome.save('nome.jpg')
    num_nf.save('num_nf.jpg')


def limpa_residuos():
    files = []
    tipos = ['.jpg', '.png']
    for tipo in tipos:
        files += [file for file in os.listdir() if tipo in file.lower()]
    for file in files:
        os.remove(file)

def rendimentos_dirf() -> int:
    tot_pags = 0
    # Cria a pasta de destino dos arquivos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for i, file in enumerate(files):
        pdf = fitz.open(file)  # Abre o arquivo pdf.
        # Atualiza o contador de páginas
        tot_pags += len(pdf)
        for i in tqdm(range(len(pdf))):
            page = pdf.load_page(i)  # Carrega a página.
            image = page.get_pixmap()  # Converte a página num objeto de imagem.
            image.save('img.jpg')  # Salva a imagem num arquivo.
            image = Image.open('img.jpg')
            """
                Pode ocorrer de a página atual ser continuação do arquivo anterior, então é necessário fazer uma verificação.
                Nas páginas de continuação, a parte inferior da página é totalmente branca, então será tentado extrair o
            texto desta seção e caso não retorne nenhum texto, a página será considerada continuação do documento anterior.
            """
            verificacao = image.crop((10, 500, 600, 750))
            verificacao.save('verificacao.jpg')
            verificacao: str = extract_text('verificacao.jpg', config='--psm 6').strip()
            # Este if irá entrar em caso o texto de verificação seja igual a '', indicando que a página é uma continuação.
            if not verificacao:
                """
                    Para evitar conflitos, é necessário primeiro abrir o arquivo anterior, em seguida criar um novo
                arquivo pdf e copiar o anterior para o novo pdf, em seguida fechar e excluir o arquivo anterior,
                e então adicionar a nova página e salvar o novo pdf.
                """
                pdf_ant = fitz.open(file_name)
                novo_pdf = fitz.open()
                novo_pdf.insert_pdf(pdf_ant)
                pdf_ant.close()
                os.remove(file_name)
                novo_pdf.insert_pdf(pdf, from_page=i, to_page=i)
                novo_pdf.save(file_name)
                continue
            #                  l     u    r    d
            #nome = image.crop((150, 185, 550, 198))
            cpf = image.crop((45, 185, 130, 198))
            #cnpj = image.crop((35, 147, 130, 160))
            #nome.save('nome.jpg')
            cpf.save('cpf.jpg')
            #cnpj.save('cnpj.jpg')

            #nome: str = extract_text('nome.jpg', config='--psm 7').strip()
            cpf: str = extract_text('cpf.jpg', config='--psm 13 -c tessedit_char_whitelist=0123456789').strip()
            #cnpj: str = extract_text('cnpj.jpg', config='--psm 13 -c tessedit_char_whitelist=0123456789').strip()
            # Remove a / do cnpj que é identificada como um '1'.
            #if len(cnpj) == 15:
            #    cnpj = cnpj[:8] + cnpj[9:]

            #file_name = 'Arquivos/' + '-'.join([nome, cpf, cnpj]) + '.pdf'
            #file_name = re.sub(r'[^a-zA-Z0-9\s./\\-]', '', file_name)
            file_name = f'Arquivos/{cpf}.pdf'
            novo_pdf = fitz.open()
            novo_pdf.insert_pdf(pdf, from_page=i, to_page=i)
            novo_pdf.save(file_name)
        pdf.close()  # Fechar o PDF para garantir que o arquivo seja liberado
    limpa_residuos()
    return tot_pags


if __name__ == '__main__':
    try:
        rendimentos_dirf()
    except Exception as e:
        print(e)
        input()
