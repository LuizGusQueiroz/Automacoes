from os import listdir, path, mkdir
from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm

# Cria a pasta de destino dos recibos
if not path.exists('Arquivos'):
    mkdir('Arquivos')

for arq in [file for file in listdir() if '.pdf' in file]:
    with open(arq, 'rb') as file:
        # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
        pdf_reader = PdfReader(file)
        pdf_writer = PdfWriter()
        lotacao = ''

        for page_pdf in tqdm(pdf_reader.pages):
            page = page_pdf.extract_text().split('\n')
            tipo = page[0][:page[0].find(' Pág.')]
            # Verifica o tipo de arquivo
            if tipo == 'Folha de Pagamento':
                lotacao_nova = page[7]
            elif tipo == 'Listagem de Férias':
                lotacao_nova = page[6]
            elif tipo == 'Listagem de Rescisão':
                lotacao_nova = page[6]
            else:
                print(tipo)
                continue
            # Verifica se já há umas pasta para o tipo
            if not path.exists(f'Arquivos/{tipo}'):
                mkdir(f'Arquivos/{tipo}')
            # Verifica se está na página de resumo ou se a lotacao for a mesma, se sim,
            # junta as páginas, caso contrário, salva o arquivo atual e cria um pdf novo.
            if 'Total Geral ' in lotacao_nova or lotacao_nova != lotacao:
                if pdf_writer.pages:
                    with open(f'Arquivos/{tipo}/{lotacao.replace('/', '')}.pdf', 'wb') as output_file:
                        pdf_writer.write(output_file)
                    pdf_writer = PdfWriter()
                lotacao = lotacao_nova
                pdf_writer.add_page(page_pdf)
            else:
                pdf_writer.add_page(page_pdf)
        # Salva o último arquivo aberto
        ...

