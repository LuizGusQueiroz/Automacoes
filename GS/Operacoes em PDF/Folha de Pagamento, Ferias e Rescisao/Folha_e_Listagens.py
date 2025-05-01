import os
from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm
import pandas as pd


def main():
    def get_tabela() -> pd.DataFrame:
        # Encontra a tabela com a relação de lotação->CNPJ.
        files = [file for file in os.listdir() if '.csv' in file]
        if len(files) != 1:
            return pd.DataFrame()
        return pd.read_csv(files[0], header=None, sep=';', encoding='latin1', names=['cod', 'nome', 'cnpj', 'tomador'])

    tot_pags = 0
    df = get_tabela()
    tem_relacao = len(df) > 0
    # Cria a pasta de destino dos recibos
    if not os.path.exists('Arquivos'):
        os.mkdir('Arquivos')

    for arq in [file for file in os.listdir() if '.pdf' in file]:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            pdf_reader = PdfReader(file)
            tot_pags += len(pdf_reader.pages)
            pdf_writer = PdfWriter()
            lotacao = ''
            i = 0
            if 'Estabelecimento:' in pdf_reader.pages[0].extract_text().split('\n')[4]:
                i = 1
            for page_pdf in tqdm(pdf_reader.pages):
                page = page_pdf.extract_text().split('\n')
                tipo = ' '.join(page[0].split()[:3])
                # Verifica o tipo de arquivo
                if tipo == 'Folha de Pagamento':
                    lotacao_nova = page[5+i]
                elif tipo == 'Listagem de Férias':
                    lotacao_nova = page[4+i]
                elif tipo == 'Listagem de Rescisão':
                    lotacao_nova = page[4+i]
                else:
                    print(tipo)
                    continue
                if len(lotacao_nova.split()[0]) > 3:
                    continue
                # Verifica se já há umas pasta para o tipo
                if not os.path.exists(f'Arquivos/{tipo}'):
                    os.mkdir(f'Arquivos/{tipo}')
                # Verifica se está na página de resumo ou se a lotacao for a mesma, se sim,
                # junta as páginas, caso contrário, salva o arquivo atual e cria um pdf novo.
                if 'Total Geral ' in lotacao_nova or lotacao_nova != lotacao:
                    if pdf_writer.pages:
                        cnpj = ''
                        if tem_relacao:
                            result = df[df['nome'] == lotacao]['cnpj']
                            if len(result) == 1:
                                cnpj = result[0]
                        file_name = f'Arquivos/{tipo}/{lotacao.replace('/', '')}-{cnpj}.pdf'
                        with open(file_name, 'wb') as output_file:
                            pdf_writer.write(output_file)
                        pdf_writer = PdfWriter()
                    lotacao = lotacao_nova
                    pdf_writer.add_page(page_pdf)
                else:
                    pdf_writer.add_page(page_pdf)
    return tot_pags



if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
