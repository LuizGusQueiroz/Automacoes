from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
from PIL import Image
import pytesseract
import cv2 as cv
import fitz
import os

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
        nome = image.crop((125, 240, 350, 255))
        num_nf = image.crop((505, 52, 535, 63))
    elif image.size == (595, 842):
        nome = image.crop((110, 235, 380, 255))
        num_nf = image.crop((520, 30, 550, 45))
    else:
        raise TypeError()
    nome.save('nome.png')
    num_nf.save('num_nf.png')


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
        nome: str = extract_text('nome.png', config='--psm 7').strip()
        num_nf: str = extract_text('num_nf.png', config='--psm 13 -c tessedit_char_whitelist=0123456789').strip()
        os.rename(file, f'NF {num_nf} - {nome}.pdf')
    # Apaga as imagens residuais.
    os.remove('img.png')
    os.remove('nome.png')
    os.remove('num_nf.png')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        input()
