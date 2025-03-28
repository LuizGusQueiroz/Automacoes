import os
from PyPDF2 import PdfReader, PdfWriter, PdfFileReader
from tqdm import tqdm
from typing import List
import pandas as pd
import sys


def get_de_para() -> pd.DataFrame:
    """
        Encontra a planilha com a relação de 'CNPJ' -> 'Nome' das empresas.
    Returns:
        pd.DataFrame: DataFrame gerado a partir da planilha com a relação.
    """
    files = [file for file in os.listdir() if '.xls' in file]
    if len(files) != 1:
        print('Tabela de clientes não encontrada.')
        input()
        sys.exit()
    df = pd.read_excel(files[0])
    df.columns = df.iloc[0]
    return df


def re_fgts_por_empresa() -> int:
    tot_pags = 0
    folder = 'Arquivos'
    # Inicializa a tabela com a relação de cnpj e nome das empresas.
    clientes: pd.DataFrame = get_de_para()
    # Cria a pasta de destino dos arquivos.
    if not os.path.exists(folder):
        os.mkdir(folder)
    # Lista todos os arquivos pdf do diretório.
    files = [file for file in os.listdir() if '.pdf' in file.lower()]
    for file in files:
        with open(file, 'rb') as file_b:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF.
            pdf = PdfReader(file_b)
            tot_pags += len(pdf.pages)
            # Itera sobre todas as páginas do PDF
            for page in tqdm(pdf.pages):
                # Extrai o texto da página no formato de uma lista de strings.
                rows: List[str] = page.extract_text().split('\n')
                # Separa a linha que contém as informações do tomador.
                row = rows[10]
                # Caso não haja 'Tomador: ' na linha 10, indica que a página atual é continuação da anterior, e deve
                # ser desconsiderada.
                if not 'Tomador: ' in row:
                    continue
                # Acessa o CNPJ.
                cnpj: str = row[row.rfind(': ')+2:]
                if cnpj == 'Sem Tomador':
                    continue
                # Separa a linha que contém as informações do empregador.
                row = rows[1]
                # Acessa o nome do empregador
                empregador = row[row.rfind(': ')+2:]
                # Verifica se já há uma pasta criada para o empregador.
                if not os.path.exists(empregador):
                    os.mkdir(empregador)
                # Procura o nome da empresa na tabela de relação.
                nome = clientes['Nome'][clientes['Inscrição'] == cnpj].values
                # Caso seja encontrada apenas uma ocorrência, o arquivo é salvo com este nome.
                if len(nome) == 1:
                    nome = nome[0].replace('/', '') + '.pdf'
                # Caso seja encontrado 0 ou mais que 1 ocorrência, o arquivo é salvo junto com outros onde
                # não se foi possível encontrar o nome.
                else:
                    nome = '_NaoEncontrados.pdf'
                # Cria um writer para salvar a página atual.
                writer = PdfWriter()
                # Adiciona a página atual ao objeto writer.
                writer.add_page(page)
                # Verifica se o arquivo com este nome já existe, caso exista, junta-o com o novo arquivo
                if nome in os.listdir(folder):
                    old_pdf = PdfReader(f'{folder}/{nome}')
                    for page in old_pdf.pages:
                        writer.add_page(page)
                # Salva a página em um novo arquivo PDF
                with open(f'{empregador}/{nome}', 'wb') as output_file:
                    writer.write(output_file)
    return tot_pags



if __name__ == '__main__':
    try:
        print(re_fgts_por_empresa())
    except Exception as e:
        print(e)
