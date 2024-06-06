from os import listdir, rename
from PyPDF2 import PdfReader

meses = {
    'JANEIRO':   '01',
    'FEVEREIRO': '02',
    'MARÇO':     '03',
    'ABRIL':     '04',
    'MAIO':      '05',
    'JUNHO':     '06',
    'JULHO':     '07',
    'AGOSTO':    '08',
    'SETEMBRO':  '09',
    'OUTUBRO':   '10',
    'NOVEMBRO':  '11',
    'DEZEMBRO':  '12'
}

for arq in  [file for file in listdir() if '.pdf' in file]:
    with open(arq, 'rb') as file:
        # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
        pdf_reader = PdfReader(file)
        # Extrai o texto do PDF
        rows = pdf_reader.pages[0].extract_text().split('\n')
    print(rows)
    # Exclui linhas em branco ou só com espaços, e em alguns casos há
    # a separação de meses e ano com um 'DE', este também será removido.
    rows = [row.replace('DE ', '').strip() for row in rows if row.replace(' ', '')]
    # Pode acontecer do ano vir separado, criando uma linha a mais, este if corrige isso
    if len(rows) == 5:
        rows[2] = rows[2] + ' ' + rows[3]
        rows[3] = rows[4]
        rows = rows[:3]
    achou = False
    # Encontra a data
    for i, row in enumerate(rows):
        if 'DIÁRIA' in row:
            data = rows[i+1].split()
            achou = True
            break
    if achou:
        # Renomeia o arquivo
        nome = f'{data[0][:2]}.{meses.get(data[-2], 'Erro')}.{data[-1]}.pdf'
        if 'Erro' in nome:
            print('*', rows)
        else:
            print(rows)
        rename(arq, nome)
    else:
        print(rows)