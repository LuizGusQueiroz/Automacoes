from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
from PIL import Image
import pytesseract
import cv2 as cv
import fitz
import os
from sys import exit

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Usuario\PycharmProjects\PyInstaller\tesseract.exe'


def pdf_split(path: str) -> None:

    with open(path, 'rb') as file:
        pdf = PdfReader(file)
        if len(pdf.pages) > 1:
            for i, page in enumerate(pdf.pages):
                writer = PdfWriter()
                writer.add_page(page)
                with open(f'{path[:-4]}-{i}.pdf', 'wb') as output:
                    writer.write(output)


def pdf_to_img(path: str, page: int = 0) -> None:

    pdf_document = fitz.open(path)  # Abre a Nota Fiscal.
    page = pdf_document.load_page(page)  # Carrega a página.
    image = page.get_pixmap()  # Converte a página num objeto de imagem.
    image.save('img.png')  # Salva a imagem num arquivo.
    image = Image.open('img.png')
    #                        l    u    r    d
    if image.size == (612, 792):
        image = image.crop((125, 240, 350, 255))
    elif image.size == (595, 842):
        image = image.crop((110, 235, 380, 255))
    else:
        raise TypeError()
    image.save('img.png')


def extract_text(path: str) -> str:
    img = cv.imread(path)
    scale_percent = 5  # Aumentar a imagem em 150%
    # Calculando o novo tamanho
    new_width = int(img.shape[1] * scale_percent)
    new_height = int(img.shape[0] * scale_percent)
    # Redimensionar a imagem proporcionalmente
    img = cv.resize(img, (new_width, new_height), interpolation=cv.INTER_LANCZOS4)
    # 1. Conversão para escala de cinza
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Executar o OCR na imagem processada
    text = pytesseract.image_to_string(img, config=r'--psm 10')
    return text


def main():
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for file in files:
        pdf_split(file)
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for file in tqdm(files):
        try:
            pdf_to_img(file)
        except TypeError:
            continue
        nome: str = extract_text('img.png').strip()
        os.rename(file, f'NF - {nome}.pdf')
    # Apaga as imagens residuais.
    os.remove('img.png')

main()
if __name__ == '__1main__':
    try:
        main()
    except Exception as e:
        print(e)
        input()
