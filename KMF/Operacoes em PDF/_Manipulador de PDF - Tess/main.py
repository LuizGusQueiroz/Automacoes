from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
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
import shutil
import fitz
import json
import time
import os

pytesseract.pytesseract.tesseract_cmd = 'configs/tess/tesseract.exe'

VERSION: str = '0.0.1'

main_msg: str = '''0: Ajuda (Informações) 
1: Identificar Automaticamente (mais lento)
2: NFs Curitiba
3: NFs Salvador
4: NFs Sorocaba
5: NFs Vitória 
6: NFs Vila Velha
'''
# Substitui o primeiro item da lista.
help_msg = '\n'.join(['\n 0: Retornar '] + main_msg.split('\n')[2:])
options: List[int] = list(range(len(main_msg.split('\n')) - 1))
# Coordenadas do local do nome do cliente e número da nota para cada dimensão de cada prefeitura.
all_sizes = {'Curitiba':   {(612, 792): [(125, 240, 350, 255), (505,  52, 535,  63)],
                            (595, 842): [(110, 235, 380, 255), (520,  30, 550,  45)]},
             'Salvador':   {(595, 842): [( 10, 198, 250, 208), (445,  22, 500,  32)]},
             'Sorocaba':   {(595, 842): [(135, 300, 370, 310), (260, 108, 276, 116)]},
             'Vitória':    {(596, 842): [(110, 255, 400, 270), (405,  38, 450,  50)]}}


def main():
    print('Manipulador de PDFs')
    print('V: ', VERSION)
    main_hub()  # inicia o menu.


def process_option(option: int) -> None:
    """
    Processa a opção do usuário.32
    """
    data = datetime.now().strftime("%d/%m/%Y")
    st = time.time()

    if option == 0:
        info_hub()
    elif option == 1:
        n_pags = identificar_nf()
        op = 'Identificar NFs'
    elif option == 2:
        n_pags = nfs_curitiba()
        op = 'NFs Curitiba'
    elif option == 3:
        n_pags = nfs_salvador()
        op = 'NFs Salvador'
    elif option == 4:
        n_pags = nfs_sorocaba()
        op = 'NFs Sorocaba'
    elif option == 5:
        n_pags = nfs_vitoria()
        op = 'NFs Vitoria'
    elif option == 6:
        n_pags = nfs_vila_velha()
        op = 'NFs Vila Velha'

    if 0 < option <= options[-1]:
        values = [[data, op, n_pags, time.time()-st]]
        salva_relatorio(values)


def main_hub():
    option: int = -1

    while option not in options:
        print('Digite uma opção de documento para separar.')
        print(main_msg)
        try:
            option = int(input('Escolha: '))
            limpa_terminal()
        except ValueError:
            pass
    process_option(option)


def info_hub() -> None:
    option: int = -1
    while option not in options:
        print('Escolha uma opção para abrir um arquivo do tipo e ler seu funcionamento.')
        print(help_msg)
        try:
            option = int(input('Escolha: '))
            limpa_terminal()
        except ValueError:
            pass
    if option not in options:
        info_hub()
    elif option != 0:
        help_doc(option)
        input('\nDigite enter para continuar')
        print('\n' * 50)
        main_hub()


def help_doc(option: int) -> None:
    os.startfile(os.getcwd() + fr'\configs\sample\{option}.pdf')
    with open('configs/READMEs.json', 'r', encoding='utf-8') as file:
        print(json.load(file)[str(option)])
    print('Um modelo deste arquivo está sendo aberto...')


def limpa_terminal() -> None:
    print('\n' * 30)


def salva_relatorio(row: List[List]):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    SAMPLE_SPREADSHEET_ID = "15gGHm67_W5maIas-4_YPSzE6R5f_CNJGcza_BJFlNBk"  # Código da planilha
    SAMPLE_RANGE_NAME = "Página1!A{}:D1000"  # Intervalo que será lido
    creds = None
    if os.path.exists("configs/token.json"):
        creds = Credentials.from_authorized_user_file("configs/token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "configs/client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("configs/token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME.format(2))
            .execute()
        )
        values = result.get("values", [])

        idx = 2 + len(values)

        result = (
            sheet.values()
            .update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME.format(idx),
                    valueInputOption='USER_ENTERED', body={"values": row})
            .execute()
        )

    except HttpError as err:
        print(err)



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


def processa_nfs(cidade: str, files: List[str] = []) -> int:
    tot_pags: int = 0
    sizes = all_sizes.get(cidade, None)
    # Verifica se a cidade foi encontrada.
    if sizes is None:
        raise TypeError('Cidade não cadastrada.')
    # Lista as NFs no diretório.
    if not files:
        files = [file for file in os.listdir() if '.pdf' in file.lower()]

    print(cidade)
    sleep(0.1)
    # Renomeia as notas.
    for file in tqdm(files):
        try:
            pdf_to_img(file, sizes)
        except TypeError:
            continue
        nome: str = extract_text('nome.jpg', config='--psm 7').strip()
        num_nf: str = extract_text('num_nf.jpg', config='--psm 13 -c tessedit_char_whitelist=0123456789').strip()

        novo_nome = f'NF {num_nf[-4:]} - {nome}.pdf'
        shutil.move(file, novo_nome)
    try:
        # Apaga as imagens residuais.
        os.remove('img.jpg')
        os.remove('nome.jpg')
        os.remove('num_nf.jpg')
    except FileNotFoundError:
        pass

    return tot_pags


def processa_outras(files: List[str] = [], tipo: str = '') -> int:
    tot_pags = len(files)
    if not tipo:
        tipo = 'Vila Velha'
    if not files:
        files = [file for file in os.listdir() if '.pdf' in file.lower()]

    if tipo == 'Vila Velha':
        print('Vila Velha')
        for file in tqdm(files):
            with open(file, 'rb') as file_b:
                pdf = PdfReader(file_b).pages[0]
                rows = pdf.extract_text().split('\n')
            num_nf = rows[6].split()[-1]
            for i, row in enumerate(rows):
                if 'Nota Fiscal de Serviços' in row:
                    nome = rows[i + 1].replace('/', '')
                    break
            nome_arq = f'NF {num_nf} - {nome}.pdf'
            os.rename(file, nome_arq)
    return tot_pags


def limpa_residuos():
    files = []
    tipos = ['.jpg', '.png']
    for tipo in tipos:
        files += [file for file in os.listdir() if tipo in file.lower()]
    for file in files:
        os.remove(file)


def identificar_nf() -> int:
    tot_pags = 0
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    cidades = all_sizes.keys()
    nfs: Dict[str, List[str]] = {cidade: [] for cidade in cidades}
    nfs['outras'] = []
    print('Identificando prefeituras...')
    for file in tqdm(files):
        # Verificar se contem texto.
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b).pages[0]
            rows = pdf.extract_text().split('\n')
            if len(rows) > 1:
                nfs['outras'].append(file)
                continue
        # Verifica de qual prefeitura é.
        pdf_document = fitz.open(file)  # Abre a Nota Fiscal.
        page = pdf_document.load_page(0)  # Carrega a página.
        image = page.get_pixmap()  # Converte a página num objeto de imagem.
        image.save('img.png')  # Salva a imagem num arquivo.
        pdf_document.close()  # Fecha o arquivo.
        image = Image.open('img.png')
        for cidade in cidades:
            if image.size in all_sizes[cidade]:
                nfs[cidade].append(file)
                break
    # Processa as notas fiscais.
    for cidade in cidades:
        if len(nfs[cidade]) > 1:
            tot_pags += processa_nfs(cidade, nfs[cidade])
    if nfs['outras']:
        tot_pags += processa_outras(nfs['outras'])
    return tot_pags


def nfs_curitiba() -> int:
    return processa_nfs('Curitiba')


def nfs_salvador() -> int:
    return processa_nfs('Salvador')


def nfs_sorocaba() -> int:
    return processa_nfs('Sorocaba')


def nfs_vitoria() -> int:
    return processa_nfs('Vitória')


def nfs_vila_velha() -> int:
    return processa_outras(tipo='Vila Velha')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        input()
    finally:
        limpa_residuos()
