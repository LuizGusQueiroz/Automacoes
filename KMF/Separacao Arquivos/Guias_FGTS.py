from os import listdir, path, mkdir
from PyPDF2 import PdfReader, PdfWriter

# Cria a pasta de destino dos recibos
if not path.exists('Guias'):
    mkdir('Guias')

for arq in [file for file in listdir() if '.pdf' in file]:
    with open(arq, 'rb') as file:
        # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
        pdf_reader = PdfReader(file)

        # Itera sobre todas as páginas do PDF
        for page_pdf in pdf_reader.pages:
            page = page_pdf.extract_text().split('\n')
            # Acessa a linha que contém o nome do empregado.
            cnpj_empregador = ''.join([char for char in page[6][-18:] if char.isnumeric()])
            nome_empregador = page[1][page[1].rfind(':')+2:]

            if 'Sem Tomador' in page[10]:
                cnpj_tomador = cnpj_empregador
            elif 'Tomador: ' in page[10]:
                cnpj_tomador = ''.join([char for char in page[10][page[10].find('Tomador: '):] if char.isnumeric()])
            else:
                continue

            nome_arq = f'{cnpj_empregador} - {nome_empregador} - {cnpj_tomador}.pdf'

            pdf_writer = PdfWriter()
            # Adiciona a página atual ao objeto PdfWriter
            pdf_writer.add_page(page_pdf)

            # Verifica se já existe a pasta do tomador
            if not path.exists(f'Guias/{cnpj_tomador}'):
                mkdir(f'Guias/{cnpj_tomador}')
            # Verifica se já há algum arquivo na pasta, caso exista, junta-o com o novo arquivo
            if listdir(f'Guias/{cnpj_tomador}'):
                old_pdf = PdfReader(f'Guias/{cnpj_tomador}/{nome_arq}')
                for page in old_pdf.pages:
                    pdf_writer.add_page(page)
            # Salva a página em um novo arquivo PDF
            with open(f'Guias/{cnpj_tomador}/{nome_arq}', 'wb') as output_file:
                pdf_writer.write(output_file)