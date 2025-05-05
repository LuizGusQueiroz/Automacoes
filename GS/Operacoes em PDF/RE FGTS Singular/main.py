from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime
from typing import List, Dict
from tqdm import tqdm
import pandas as pd
import openpyxl
import time
import os


class Aut:
    def __init__(self, dest: str = 'Arquivos', not_found_name: str = '_Nao_Encontrados',
                 not_found_empr: str = 'Sem Empregador'):
        self.dest: str = dest  # Diretório de destino dos arquivos.
        self.not_found_name: str = not_found_name  # Nome padrão para nomes não encontrados.
        self.not_found_empr: str = not_found_empr  # Nome padrão para empregador não encontrado.
        self.rel: Dict[str, str] = self.get_relacao()
        self.n_pags: int = 0  # Total de páginas processadas.

    def salva_relatorio(self, tempo_exec) -> None:
        row = [[datetime.now().strftime("%d/%m/%Y"), 'RE FGTS', self.n_pags, tempo_exec]]
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
                    "configs/client.json", SCOPES
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

    def get_relacao(self) -> Dict[str, str]:
        """ Encontra a tabela com a relação de CNPJ -> Nome da empresa."""
        # Lista os arquivos excel no diretório e verifica se há exatamente 1.
        files = [file for file in os.listdir() if '.xls' in file.lower()]
        if len(files) != 1:
            raise Exception('Tabela de clientes não encontrada.')
        df = pd.read_excel(files[0])
        df.columns = ['Código', 'Nome', 'Inscrição']
        # Converte a relação para um dicionário, para o nome de tomador pode ser encontrado com
        # nome = rel.get(cnpj, 'não encontrado').
        rel: Dict[str, str] = df.drop_duplicates(subset='Inscrição').set_index('Inscrição')['Nome'].to_dict()
        # Define um nome para casos sem tomador.
        rel['Sem Tomador'] = self.not_found_name
        return rel

    def init_dir(self) -> None:
        # Cria a pasta de destino das guias.
        if not os.path.exists(self.dest):
            os.mkdir(self.dest)

    def get_nome(self, rows: List[str]) -> str:
        # Encontra o cnpj do tomador e acha o nome correspondente.
        for row in rows:
            if 'TotalTomador' in row:
                cnpj: str = row.split()[-1]
                nome: str = self.rel.get(cnpj, self.not_found_name)
                break
        else:
            nome = self.not_found_name
        return nome

    def get_empregador(self, rows: List[str]) -> str:
        for row in rows:
            if 'Nome Empregador:' in row:
                empregador = ' '.join(row.split()[5:])
                # Remove caracteres especiais.
                for char in ['\\', '/', '.']:
                    empregador = empregador.replace(char, '')
                return empregador
        return self.not_found_empr

    def run(self) -> None:
        st = time.time()
        self.processa_pdfs()
        exec_time = time.time() - st
        self.salva_relatorio(exec_time)

    def processa_pdfs(self) -> None:
        self.init_dir()  # Inicializa o diretório de destino de arquivos.
        n_encontrados = PdfWriter()  # Writer para arquivos onde o nome não foi encotrado.
        not_found_name = f'{self.dest}/{self.not_found_name}.pdf'
        # Lista todos os arquivos pdf no diretório.
        files = [file for file in os.listdir() if '.pdf' in file.lower()]
        for file in files:
            with open(file, 'rb') as file_bin:
                # Cria um objeto PdfReader para ler o conteúdo do arquivo PDF
                pdf = PdfReader(file_bin)
                self.n_pags += len(pdf.pages)
                # Itera sobre todas as páginas do PDF.
                for page in tqdm(pdf.pages):
                    # Converte o texto do pdf em uma lista do conteúdo das linhas.
                    rows: List[str] = page.extract_text().split('\n')
                    nome: str = self.get_nome(rows)
                    empregador: str = self.get_empregador(rows)
                    # Verifica se a pasta para o empregador já existe.
                    if not os.path.exists(f'{self.dest}/{empregador}'):
                        os.mkdir(f'{self.dest}/{empregador}')

                    file_name = f'{self.dest}/{empregador}/{nome}.pdf'
                    # Verifica se é um arquivo com nome não encontrado.
                    # Este tratamento não previne erros, apenas garante performace,
                    # para não ser necessário sempre reabrir este arquivo e salvar suas páginas novamente.
                    if self.not_found_name in file_name:
                        n_encontrados.add_page(page)
                        continue
                    # Cria um writer.
                    writer = PdfWriter()
                    # Verifica se o arquivo com este nome já existe,
                    # caso exista, junta todas as suas páginas com a atual.
                    if os.path.exists(file_name):
                        writer.append(file_name)
                    # Adiciona a página atual ao objeto PdfWriter.
                    writer.add_page(page)
                    # Salva o arquivo.
                    with open(file_name, 'wb') as output:
                        writer.write(output)
        # Salva o arquivo de arquivos não encontrados.
        with open(not_found_name, 'wb') as output:
            n_encontrados.write(output)


if __name__ == '__main__':
    try:
        aut = Aut()
        aut.run()
    except Exception as e:
        print(e)
        input()

