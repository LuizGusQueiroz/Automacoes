from os import listdir, path, mkdir
from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm


def main() -> None:
    """
    Lista todos os arquivos PDF no diretório atual (só irá funcionar para Listagens de Conferência)
    e separa em subarquivos, agrupados pela lotação.
    """
    # Cria a pasta de destino dos recibos
    if not path.exists('Arquivos'):
        mkdir('Arquivos')

    for arq in [file for file in listdir() if '.pdf' in file]:
        folder_name = arq.replace('.pdf', '').replace('/', '')
        if not path.exists(f'Arquivos/{folder_name}'):
            mkdir(f'Arquivos/{folder_name}')

        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            pdf_writer = PdfWriter()
            lotacao = ''

            for page_pdf in tqdm(pdf_reader.pages):
                page = page_pdf.extract_text().split('\n')
                # Acessa a lotação
                lotacao_nova = page[6]
                # Verifica se a lotação é a mesma, se for, junta as páginas,
                # caso contrário, salva o arquivo atual e cria um pdf novo.
                if lotacao_nova != lotacao:
                    if pdf_writer.pages:
                        with open(f'Arquivos/{folder_name}/{lotacao}.pdf', 'wb') as output_file:
                            pdf_writer.write(output_file)
                        pdf_writer = PdfWriter()
                    lotacao = lotacao_nova
                    pdf_writer.add_page(page_pdf)
                else:
                    pdf_writer.add_page(page_pdf)
            # Não é necessário salvar o último arquivo em memória, pois é apenas o resumo.


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        input()
