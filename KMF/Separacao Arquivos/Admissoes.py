from os import listdir, path, mkdir
from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm

# Cria a pasta de destino dos documentos
if not path.exists('Documentos'):
    mkdir('Documentos')

for arq in [file for file in listdir() if '.pdf' in file]:
    with open(arq, 'rb') as file:
        # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF.
        pdf_reader = PdfReader(file)

        # Para cada página, identifica o tipo de documento e o nome do funcionário.
        for pag in tqdm(pdf_reader.pages):
            rows = pag.extract_text().split('\n')
            # Encontra o título do documento.
            idx = 0
            while not rows[idx].strip():
                idx += 1
            titulo = rows[idx].strip()
            # Acessa o nome com base no tipo de documento.
            if titulo == 'DECLARAÇÃO DE DEPENDENTES PARA FINS DE IMPOSTO DE RENDA':
                nome = rows[2]
            elif titulo == 'TERMO LDPD':
                row = rows[3]
                nome = row[35:row.find(',', 35)].replace('_', '')
            elif titulo == 'R E C I B O  D E  E N T R E G A  D A  C A R T E I R A  D E  T R A B A L H O':
                for row in rows:
                    if '(Carimbo e visto da empresa)' in row:
                        nome = row[28:-12]
                        break
            elif titulo == 'CTPS DIGITAL':
                row = rows[3]
                nome = row[row.find(' '):row.find(',', 4)]
                # Remove espaços entre os nomes.
                nome = ' '.join(nome.split())
            elif titulo == 'TERMO DE COMPROMISSO DE VALE-TRANSPORTE':
                nome = rows[8]
            elif titulo == 'TERMO COLETIVO DE CESSÃO GRATUITA DE USO DE IMAGEM PARA DIVULGAÇÃO':
                nome = rows[30][11:]
            elif titulo == 'REGISTRO DE EMPREGADONúmero:':
                nome = rows[19][:-14]
            elif titulo == 'Termo de Responsabilidade':
                nome = rows[6][:-10]
            elif titulo == 'Contrato de Experiência de Trabalho':
                row = rows[2]
                nome = row[row.find(',')+1:row.find(' p', row.find(','))].strip()
                # Remove espaços entre os nomes
                nome = ' '.join(nome.split())
            elif titulo[:20] == 'A Controladora fica ':
                nome = rows[30]
            else:
                print(f'Documento {titulo} não reconhecido!')
                input()
                continue

            file_name = f'Documentos\\{nome}.pdf'
            pdf_writer = PdfWriter()
            # Verifica se já existe um arquivo para este funcionário
            if path.exists(file_name):
                pdf_reader_temp = PdfReader(file_name)
                # Copia todas as páginas do documento do funcionário para o writer
                for page_num in range(len(pdf_reader_temp.pages)):
                    pdf_writer.add_page(pdf_reader_temp.pages[page_num])

            # Adiciona a página atual
            pdf_writer.add_page(pag)
            # Salva o arquivo
            with open(file_name, "wb") as output_pdf:
                pdf_writer.write(output_pdf)
