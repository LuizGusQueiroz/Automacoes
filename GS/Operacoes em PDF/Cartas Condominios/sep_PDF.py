from PyPDF2 import PdfReader, PdfWriter

diretorio = r'C:\Users\Usuario\PycharmProjects\NOTAS\SINGULAR\Separa PDF\PDFs'

with open('cartas.pdf', 'rb') as file:
    # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
    pdf_reader = PdfReader(file)
    # Encontra a linha que contém o nome do condomínio
    pags = pdf_reader.pages[0].extract_text().split('\n')
    for i in range(20):
        print(i, pags[i])
    lin = int(input('\nLinha com o nome do Condomínio: '))

    # Itera sobre todas as páginas do PDF
    for i in range(len(pdf_reader.pages)):
        pag = pdf_reader.pages[i].extract_text().split('\n')
        # Acessa a linha que contém o nome do condomínio
        nome = pag[lin]
        nome = nome.replace('/', '-')

        pdf_writer = PdfWriter()

        # Adiciona a página atual ao objeto PdfWriter
        pdf_writer.add_page(pdf_reader.pages[i])

        # Salva a página em um novo arquivo PDF
        with open(fr'{diretorio}/{nome}.pdf', 'wb') as output_file:
            pdf_writer.write(output_file)