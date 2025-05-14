import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from tqdm import tqdm

def enviar_emails_por_pasta(pasta_base, destinatario):
    remetente = "teste001py@gmail.com"
    assunto_base = "Boletos e Notas Fiscais"
    senha = "ebst dqbm ycpw bdqt"
    
    if not os.path.exists(pasta_base):
        print(f"Erro: Pasta base '{pasta_base}' não encontrada!")
        return False
    
    subpastas = [d for d in os.listdir(pasta_base) if os.path.isdir(os.path.join(pasta_base, d))]
    
    if not subpastas:
        print("Erro: Nenhuma subpasta encontrada na pasta base!")
        return False
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha)
    except Exception as e:
        print(f"Erro ao conectar ao servidor SMTP: {e}")
        return False
    
    with tqdm(subpastas, desc="Enviando emails", unit="CNPJ") as pbar:
        for cnpj in pbar:
            pbar.set_postfix(CNPJ=cnpj)
            
            pasta_cnpj = os.path.join(pasta_base, cnpj)
            arquivos = [f for f in os.listdir(pasta_cnpj) if os.path.isfile(os.path.join(pasta_cnpj, f))]
            
            if not arquivos:
                pbar.write(f"Aviso: Pasta {cnpj} está vazia - pulando...")
                continue
            
            msg = MIMEMultipart()
            msg['From'] = remetente
            msg['To'] = destinatario
            msg['Subject'] = f"{assunto_base} - CNPJ: {cnpj}"
            
            corpo = f"""Bom dia,

Segue em anexo os boletos e envios da empresa Singular referentes ao CNPJ: {cnpj}.

Atenciosamente,
Time de Contabilidade"""
            
            msg.attach(MIMEText(corpo, 'plain'))
            
            anexos_com_sucesso = 0
            for arquivo in tqdm(arquivos, desc=f"Anexando arquivos {cnpj}", leave=False):
                caminho_completo = os.path.join(pasta_cnpj, arquivo)
                try:
                    with open(caminho_completo, "rb") as anexo:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(anexo.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename="{arquivo}"')
                        msg.attach(part)
                    anexos_com_sucesso += 1
                except Exception as e:
                    pbar.write(f"Erro ao anexar {arquivo}: {e}")
            
            if anexos_com_sucesso == 0:
                pbar.write(f"Aviso: Nenhum arquivo válido em {cnpj} - pulando envio...")
                continue
            
            try:
                server.sendmail(remetente, destinatario, msg.as_string())
                pbar.write(f"Email enviado para CNPJ: {cnpj}")
                pbar.write(f"Arquivos anexados: {anexos_com_sucesso}")
                pbar.write("----------------------------------------")
            except Exception as e:
                pbar.write(f"Falha ao enviar email para {cnpj}: {e}")
    
    server.quit()
    return True

if __name__ == "__main__":
    print("=== Enviador Automático de Emails por CNPJ ===")
    destinatario = input("Digite o email do destinatário: ")
    pasta_base = 'arquivos_organizados/Pastas_Mescladas'
    
    print(f"\nConfiguração:")
    print(f"Remetente: teste001py@gmail.com")
    print(f"Destinatário: {destinatario}")
    print("Assunto base: Boletos e Notas Fiscais")
    
    print(f"\nProcessando pastas de CNPJ em: {pasta_base}")
    enviar_emails_por_pasta(pasta_base, destinatario)