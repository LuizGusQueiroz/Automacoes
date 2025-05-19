import os
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def enviar_email(remetente, senha, destinatario, assunto, corpo, arquivos=[]):
   
    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = assunto
    
    msg.attach(MIMEText(corpo, 'plain'))
    
    for arquivo in arquivos:
        with open(arquivo, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(arquivo))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(arquivo)}"'
        msg.attach(part)
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587) 
        server.login(remetente, senha)
        server.sendmail(remetente, destinatario, msg.as_string())
        server.quit()
        print(f"E-mail enviado com sucesso para {destinatario}!")
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail para {destinatario}: {str(e)}")
        return False

def processar_cnpjs():
    df = pd.read_excel("GS/envio_boletos_nfs/usuario_senha.xlsx")
    df.columns = [str(col).strip().upper() for col in df.columns]
    
    df['CNPJ'] = df['CNPJ'].astype(str).str.strip().str.zfill(14)
    dados = df.set_index('CNPJ').to_dict('index')

    base_path = "GS/arquivos_organizados/Pastas_Mescladas"
    pastas = os.listdir(base_path)
    
    for pasta in pastas:
        if not (pasta.isdigit()):
            continue
            
        caminho_pasta = os.path.join(base_path, pasta)
        
        if not os.path.isdir(caminho_pasta):
            continue
            
        print(f"\nProcessando CNPJ: {pasta}")
        
        if pasta in dados:
            info = dados[pasta]
            remetente = info.get('REMENTENTE', '').strip()
            senha = info.get('SENHA', '').strip()
            destinatario = info.get('DESTINATARIO', '').strip()
            
            if not remetente or not senha or not destinatario:
                print(f"Dados incompletos para envio de e-mail.{pasta}")
                continue
            
            arquivos = []
            for arquivo in os.listdir(caminho_pasta):
                caminho_arquivo = os.path.join(caminho_pasta, arquivo)
                if os.path.isfile(caminho_arquivo):
                    arquivos.append(caminho_arquivo)
            
            if not arquivos:
                print(f"Nenhum arquivo encontrado para enviar. {pasta}")
                continue
            
            assunto = f"Documentos para o CNPJ {pasta}"
            corpo = f"""

Segue em anexo os documentos referentes ao CNPJ {pasta}.

Atenciosamente,
Sistema de Envio Automático"""
            
            print(f"Preparando para enviar {len(arquivos)} arquivo(s) para {destinatario}...")
            enviar_email(remetente, senha, destinatario, assunto, corpo, arquivos)
        else:
            print("CNPJ não encontrado na planilha de dados.")

if __name__ == "__main__":
    processar_cnpjs()