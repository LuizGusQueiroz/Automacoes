"""
O E-mail precisa ter a autenticação de dois fatores, com isto ativado, poderá ser
acessada uma seção de 'Senha para apps', lá deverá ser criado um app e a senha
fornecida pelo google deverá ser utilizada nesta conexão.
"""
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import path, listdir
from PyPDF2 import PdfReader
import pandas as pd
import smtplib
import sys


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
    with open(path, 'rb') as file:
        # Cria um objeto PdfFileReader para ler o conteúdo do arquivo PDF
        boleto = PdfReader(file)
        # Cada boleto tem apenas uma página, então apenas a primeira página precisa ser considerada
        rows = boleto.pages[0].extract_text().split('\n')
    # Acessa o CNPF e remove os símbolos '.', '/' e '-'.
    cnpj = rows[14].split()[-1]
    cnpj = int(''.join([char for char in cnpj if char.isnumeric()]))

    cliente = clientes['CLIENTE'][clientes['CNPJ'] == cnpj].values[0]
    destinatarios = clientes['EMAIL'][clientes['CNPJ'] == cnpj].values[0]
    # Deixa os emails no formato 'email1@gmail.com, email2@gmail.com, email3@gmail.com'.
    destinatarios = ', '.join([email for email in destinatarios.split(' ') if email])  # Remove itens em branco

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
    clientes = pd.read_excel('Clientes.xlsx')
    email, senha = get_creds()
    conn = start_conn(email, senha)

    files = [f'Boletos/{file}' for file in listdir('Boletos') if '.pdf' in file]
    for arq in files:
        cliente, destinatarios = read_boleto(arq, clientes)
        destinatarios = 'luizgus@alu.ufc.br'
        # Cria a mensagem.
        msg = MIMEMultipart()
        msg['From'] = email # Quem envia
        msg['To'] = 'luizgus@alu.ufc.br' #destinatarios
        msg['Subject'] = 'Boletos' # Assunto do E-mail
        # Ajusta o corpo da mensagem com base no template
        msg_html = template.format(cliente=cliente)
        # Anexar o conteúdo HTML ao email
        msg.attach(MIMEText(msg_html, 'html'))

        # Anexa o PDF.
        with open(arq, 'rb') as file:
            pdf = MIMEApplication(file.read(), _subtype='pdf')
            pdf.add_header('Content-Disposition', 'attachment', filename=path.basename(arq))
            msg.attach(pdf)
        # Envia o e-mail.
        conn.sendmail(email, destinatarios, msg.as_string())
        print(f'{arq[8:]} enviado para os emails: {destinatarios}')
    # Encerra a conexão
    conn.quit()


if __name__ == '__main__':
    try:
        main()
    except smtplib.SMTPAuthenticationError:
        print('Login ou Email inválido!')
        input()

