"""
O E-mail precisa ter a autenticação de dois fatores, com isto ativado, poderá ser
acessada uma seção de 'Senha para apps', lá deverá ser criado um app e a senha
fornecida pelo google deverá ser utilizada nesta conexão.
"""
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import path, listdir, mkdir, rename
from PyPDF2 import PdfReader
from typing import List
import pandas as pd
import smtplib
import sys


def get_tabela_clientes() -> pd.DataFrame:
    """
    Encontra a tabela de clientes, comparando as colunas da tabela com
    o modelo definido ['CNPJ', 'CLIENTE', 'EMAIL'].
    """
    files = [file for file in listdir() if '.xls' in file]
    for file in files:
        df = pd.read_excel(file)
        if set(df.columns) == {'CNPJ', 'CLIENTE', 'EMAIL'}:
            return df
    print('Tabela de clientes não encontrada!')
    input()
    sys.exit()


def renomeia_pdfs(tipo: str) -> set[int]:
    cnpjs = set()
    arqs = [f'{tipo}/{arq}' for arq in listdir(tipo)]
    for arq in arqs:
        with open(arq, 'rb') as file:
            # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
            arq_pdf = PdfReader(file)
            # Cada arquivo tem apenas uma página, então apenas a primeira página precisa ser consider
            rows = arq_pdf.pages[0].extract_text().split('\n')
        try:
            cnpj, num_nf = get_cnpj_e_numnf(rows, tipo)
        except TypeError:
            print(f'Erro em {arq}')
        if tipo == 'Boletos':
            rename(arq, f'{tipo}/{cnpj}.pdf')
        elif tipo == 'Notas':
            rename(arq, f'{tipo}/{cnpj}-{num_nf}.pdf')
        cnpjs.add(cnpj)
    return cnpjs


def get_cnpj_e_numnf(rows: List[str], tipo: str) -> (str, str):
    cnpj, num_nf = '---', '---'
    if tipo == 'Boletos':
        if rows[0] == 'Endereço do Beneficiário ':  # Singular grafeno
            cnpj = rows[14].split()[-1]
        elif rows[0] == 'Beneficiário CPF/CNPJ':  # 4S
            cnpj = rows[10].split()[-1]
        elif rows[0] == 'Quer emitir boletos de forma rápida? Entre em contato conosco: www.mentorebank.com.brValor Vencimento':
            cnpj = rows[26].split()[-1][:-6]
        else:
            raise TypeError
    elif tipo == 'Notas':
        num_nf = rows[4]
        for row in rows:
            if 'Retenções Federais' in row:
                cnpj = row.split()[-1][-18:]
                break
    # Remove os símbolos '.', '/' e '-' do CNPJ.
    cnpj = int(''.join([char for char in cnpj if char.isnumeric()]))
    return cnpj, num_nf


def get_creds() -> (str, str):
    """
    Acessa o arquivo config.txt e extrai dele um login e uma senha.
    O conteúdo do arquivo config.txt deve estar no formato:
    email: ExemploEmail@gmail.com
    senha: ExemploSenha
    Para este exemplo, o retorno seria a tupla
    ('ExemploEmail@gmail.com', 'ExemploSenha')
    """
    with open('config.txt', 'r') as file:
        # Cria um dicionário a partir do arquivo
        dados = {chave: valor.strip() for chave, valor in [row.split(':') for row in file.read().split('\n')]}

        email = dados['email']
        senha = dados['senha']

    return email, senha


def start_conn(email: str, senha: str) -> smtplib.SMTP:
    """
    Estabelece uma conexão com o servidor utilizando o email e senha fornecidos.
    Por padrão, a conexão é estabelecida com o gmail.
    """
    conn = smtplib.SMTP('smtp.gmail.com', 587)
    # Habilita a conexão com o servidor.
    conn.starttls()
    # Autentica no servidos.
    conn.login(email, senha)
    return conn


def read_boleto(path: str, clientes: pd.DataFrame) -> (str, str):
    """
    Recebe um caminho de um boleto no formato PDF e acessa o nome do cliente e o seu CNPJ.
    Pela tabela clientes, é encontrado os destinatários com base no CNPJ encontrado.
    """
    tipo: str = path[:path.find('/')]
    with open(path, 'rb') as file:
        # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
        boleto = PdfReader(file)
        # Cada boleto tem apenas uma página, então apenas a primeira página precisa ser considerada
        rows: list[str] = boleto.pages[0].extract_text().split('\n')
    # Acessa o CNPJ do arquivo.
    try:
        cnpj, _ = get_cnpj_e_numnf(rows, tipo)
    except TypeError:
        print(f'Erro em {path}')
        return {0}

    cliente = clientes['CLIENTE'][clientes['CNPJ'] == cnpj].values[0]
    destinatarios = clientes['EMAIL'][clientes['CNPJ'] == cnpj].values[0].replace(',', '').split()

    destinatarios = [email for email in destinatarios if email]  # Remove itens em branco

    return cliente, destinatarios


def main():
    template = '''
    <html>
      <body>
        <p>Olá {cliente}!
           Seguem o Boleto e Nota Fiscal deste mês!<p>
      </body>
    </html>
    '''
    # Cria as pastas de origem dos arquivos.
    if not path.exists('Boletos'):
        mkdir('Boletos')
    if not path.exists('Notas'):
        mkdir('Notas')

    cnpjs_bol = renomeia_pdfs('Boletos')
    cnpjs_not = renomeia_pdfs('Notas')
    cnpjs = cnpjs_bol | cnpjs_not

    clientes = get_tabela_clientes()
    email, senha = get_creds()
    conn = start_conn(email, senha)

    for cnpj in cnpjs:
        files = [f'Boletos/{file}' for file in listdir('Boletos') if str(cnpj) in file] + \
                [f'Notas/{file}' for file in listdir('Notas') if str(cnpj) in file]
        try:
            cliente, destinatarios = read_boleto(files[0], clientes)
        except IndexError:
            print(f'CNPJ não encontrado: {[cnpj]}')
            continue

        # Verifica se há apenas a nota sem boleto, caso seja este caso, a nota não é enviada.
        tem_boleto = False
        for file in files:
            if 'Boleto' in file:
                tem_boleto = True
                break
        if not tem_boleto:
            print(f'Há apenas o boleto para {[cnpj]}')
            continue

        # Mandas a mensagem para cada destinatário:
        for destinatario in destinatarios:
            # Cria a mensagem.
            msg = MIMEMultipart()
            msg['From'] = email  # Quem envia
            msg['To'] = destinatario
            msg['Subject'] = f'Faturamento {cliente}'  # Assunto do E-mail
            # Ajusta o corpo da mensagem com base no template.
            msg_html = template.format(cliente=cliente)
            # Anexar o conteúdo HTML ao email
            msg.attach(MIMEText(msg_html, 'html'))

            # Anexa os PDFs.
            for arq in files:
                with open(arq, 'rb') as file:
                    pdf = MIMEApplication(file.read(), _subtype='pdf')
                    pdf.add_header('Content-Disposition', 'attachment', filename=path.basename(arq))
                    msg.attach(pdf)
            # Envia o e-mail.
            conn.sendmail(email, destinatario, msg.as_string())
            print(f'{files} enviado para o email: {destinatario}')

    # Encerra a conexão
    conn.quit()
    print('-----Fim-----')


if __name__ == '__main__':
    try:
        main()
    except smtplib.SMTPAuthenticationError:
        print('Login ou Email inválido!')
    except Exception as e:
        print(e)
    finally:
        input()
