from PyPDF2 import PdfReader, PdfWriter
from typing import List
from tqdm import tqdm
import os


def f21() -> int:
    """
        Separa todos os arquivos .pdf que sejam recibos de pagamento emitidos pelo sistema Protheus
        com base no funcionário, criando um arquivo individual para cada novo funcionário.
    Returns:
        (int): O total de páginas somadas de todos os arquivos pdf.
    """
    # inicia a contagem de páginas
    n_pags = 0
    # Cria a pasta de destino dos arquivos separados.
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')
    # Lista todos os arquivos .pdf no diretório.
    # O 'file.lower()' previne casos de arquivos salvos como 'file.PDF'.
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for file in files:
        # Abre o arquivo pdf.
        with open(file, 'rb') as file_b:
            pdf = PdfReader(file_b)
            # Soma o total das suas páginas.
            n_pags += len(pdf.pages)
            # Percorre as páginas do pdf.
            for page in tqdm(pdf.pages):
                # Extrai o texto do pdf na forma de uma lista de strings.
                rows: List[str] = page.extract_text().split('\n')
                # Acessa o nome e a matrícula, que estão na terceira linha.
                # Ao dar um split na terceira linha, os 4 primeiros e os 2 últimos itens são de cabeçalho,
                # restando o nome entre os items 5 até o -3.
                # Já a matrícula é o segundo item dessa linha.
                nome = ' '.join(rows[3].split()[5:-3])
                matricula = rows[3].split()[2]
                centro_custo = ' '.join(rows[2].split()[5:-1])
                centro_custo = centro_custo.replace('/', '')
                cnpj = rows[1].split()[-1]
                # Formata o nome do arquivo com os dados encontrados.
                file_name = f'Arquivos/{nome}-{matricula}-{centro_custo}-{cnpj}.pdf'
                # Salva a página em um arquivo separado.
                writer = PdfWriter()
                writer.add_page(page)
                with open(file_name, 'wb') as output:
                    writer.write(output)
    return n_pags
