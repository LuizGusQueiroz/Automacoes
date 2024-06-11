"""
O E-mail precisa ter a autenticação de dois fatores, com isto ativado, poderá ser
acessada uma seção de 'Senha para apps', lá deverá ser criado um app e a senha
fornecida pelo google deverá ser utilizada nesta conexão.
"""
from os import path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


with open('config.txt', 'r') as file:
    exec(file.read())

# Estabelece uma conexão com o servidor.
conn = smtplib.SMTP('smtp.gmail.com', 587)
# Habilita a conexão com o servidor.
conn.starttls()
# Autentica no servidos.
conn.login(email, senha)
# Cria a mensagem.
msg = MIMEMultipart()
msg['From'] = email
msg['To'] = ", ".join(destinatarios)
msg['Subject'] = 'Assunto do E-mail'
# Corpo do e-mail.
conteudo = 'Conteúdo do E-mail.'
msg.attach(MIMEText(conteudo, 'plain'))
# Anexa um PDF.
pdf_path = 'TRIX LOG LTDA-14427.pdf'
with open(pdf_path, 'rb') as file:
    pdf = MIMEApplication(file.read(), _subtype='pdf')
    pdf.add_header('Content-Disposition', 'attachment', filename=path.basename(pdf_path))
    msg.attach(pdf)
# Envia o e-mail.
conn.sendmail(email, destinatarios, msg.as_string())
# Encerra a conexão
conn.quit()
