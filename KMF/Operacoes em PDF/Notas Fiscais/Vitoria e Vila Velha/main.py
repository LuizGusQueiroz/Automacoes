from PyPDF2 import PdfReader
from tqdm import tqdm
from PIL import Image
import pytesseract
import cv2 as cv
import fitz
import os


pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Usuario\PycharmProjects\PyInstaller\tesseract.exe'


def main():
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for file in tqdm(files):
        # Verificar qual nota é
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b).pages[0]
            rows = pdf.extract_text().split('\n')
        vila_velha = len(rows) != 1
        if vila_velha:  # Vila velha
            num_nf = rows[6].split()[-1]
            for i,row in enumerate(rows):
                if 'Nota Fiscal de Serviços' in row:
                    nome = rows[i+1].replace('/', '')
                    break
        else:  # Vitória
            pdf_to_img(file)
            nome: str = extract_text('nome.png', config='--psm 7').strip()
            num_nf: str = extract_text('num_nf.png', config='--psm 13 -c tessedit_char_whitelist=0123456789').strip()
        os.rename(file, f'{nome}-{num_nf}.pdf')
    apaga_residuos()


def pdf_to_img(path: str, page: int = 0) -> None:

    pdf_document = fitz.open(path)  # Abre a Nota Fiscal.
    page = pdf_document.load_page(page)  # Carrega a página.
    image = page.get_pixmap()  # Converte a página num objeto de imagem.
    image.save('img.png')  # Salva a imagem num arquivo.
    image = Image.open('img.png')
    #                   l    u    r    d
    nome = image.crop((110, 255, 400, 270))
    num_nf = image.crop((405, 38, 450, 50))
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


def apaga_residuos() -> None:
    for file in os.listdir():
        if '.png' in file:
            os.remove(file)


main()
if __name__ == '__main__0':
    try:
        main()
    except Exception as e:
        print(e)
        input()
