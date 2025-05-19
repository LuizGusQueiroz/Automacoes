import os
import re
import shutil
from PyPDF2 import PdfReader
from tqdm import tqdm
from typing import List, Optional, Dict
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd

class GerenciadorDocumentos:
    def __init__(self):
        self.base_dir = 'GS/CONDOMINIAIS'
        self.boletos_dir = os.path.join(self.base_dir, 'BOLETOS')
        self.nfs_dir = os.path.join(self.base_dir, 'NOTA FISCAL')
        self.organizados_dir = 'GS/arquivos_organizados'
        
        self.CNPJ_PATTERN = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'
        self.CNPJ_IGNORADO = "16.707.848/0001-95"
        self.CNPJ_PARA_EMAIL = {
            "00247732000180": "jcczzin223@gmail.com",
            "00675570000181": "joaquimoliveira2@edu.unifor.br",
            "01727202000100": "luizgusqueiroz@gmail.com"
        }
        self.email_credenciais = self._ler_credenciais_email()

#ler o email e senha do arquivo readme.txt

    def _ler_credenciais_email(self, arquivo=None) -> Dict[str, Optional[str]]:
        """Lê as credenciais de email de um arquivo de texto"""
        if arquivo is None:
            arquivo = os.path.join('GS', 'envio_boletos_nfs', 'readme.txt')
        
        credenciais = {'usuario': None, 'senha': None}
        
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                for linha in f:
                    linha = linha.strip()
                    if not linha:
                        continue
                    if linha.lower().startswith('usuario'):
                        credenciais['usuario'] = linha.split('=')[1].strip()
                    elif linha.lower().startswith('senha'):
                        credenciais['senha'] = linha.split('=')[1].strip()
                    if credenciais['usuario'] and credenciais['senha']:
                        break
        except FileNotFoundError:
            print(f"\nErro: Arquivo {arquivo} não encontrado!")
        except Exception as e:
            print(f"\nErro ao ler o arquivo de credenciais: {e}")
        
        return credenciais

    def criar_diretorio(self, caminho: str) -> None:
        os.makedirs(caminho, exist_ok=True)

    def limpar_cnpj(self, cnpj: str) -> str:
        return re.sub(r'\D', '', cnpj)

    def extrair_texto_pdf(self, caminho_pdf: str) -> List[str]:
        if not os.path.exists(caminho_pdf):
            return []
        with open(caminho_pdf, 'rb') as arquivo:
            leitor = PdfReader(arquivo)
            primeira_pagina = leitor.pages[0]
            return primeira_pagina.extract_text().split('\n')

    def encontrar_cnpj_boleto(self, linhas_texto: List[str]) -> Optional[str]:
        cnpjs = []
        for linha in linhas_texto:
            if 'CNPJ:' in linha or 'CPF/CNPJ:' in linha:
                partes = linha.split()
                if partes:
                    cnpj_bruto = partes[-1]
                    cnpj_formatado = self.limpar_cnpj(cnpj_bruto)
                    if len(cnpj_formatado) in (11, 14):
                        cnpjs.append(cnpj_formatado)
        return cnpjs[1] if len(cnpjs) >= 2 else cnpjs[0] if cnpjs else None

    def encontrar_cnpjs_nf(self, texto: str) -> List[str]:
        cnpjs = re.findall(self.CNPJ_PATTERN, texto)
        return [c for c in cnpjs if c != self.CNPJ_IGNORADO]

    def organizar_boletos(self) -> None:
        destino = os.path.join(self.organizados_dir, 'Boletos_organizados')
        self.criar_diretorio(destino)
        arquivos = [f for f in os.listdir(self.boletos_dir) if f.lower().endswith('.pdf')]

        if not arquivos:
            print("\nNenhum arquivo PDF encontrado na pasta de boletos.")
            return

        print("\nOrganizando boletos por CNPJ...")
        for arquivo in tqdm(arquivos, desc='Processando boletos'):
            caminho_completo = os.path.join(self.boletos_dir, arquivo)
            linhas = self.extrair_texto_pdf(caminho_completo)
            cnpj = self.encontrar_cnpj_boleto(linhas)
            if not cnpj:
                print(f"\nAtenção: Não foi possível identificar CNPJ no arquivo {arquivo}")
                continue
            pasta_cnpj = os.path.join(destino, cnpj)
            self.criar_diretorio(pasta_cnpj)
            shutil.copy2(caminho_completo, os.path.join(pasta_cnpj, arquivo))

    def organizar_nfs(self) -> None:
        destino = os.path.join(self.organizados_dir, 'nfs_organizados')
        self.criar_diretorio(destino)
        destino_sem_cnpj = os.path.join(destino, 'nfs sem cnpj')
        self.criar_diretorio(destino_sem_cnpj)
        arquivos = [f for f in os.listdir(self.nfs_dir) if f.lower().endswith('.pdf')]

        if not arquivos:
            print("\nNenhum arquivo PDF encontrado na pasta de NF-es.")
            return

        print("\nOrganizando NF-es por CNPJ...")
        for arquivo in tqdm(arquivos, desc='Processando NF-es'):
            caminho_completo = os.path.join(self.nfs_dir, arquivo)
            try:
                with open(caminho_completo, 'rb') as f:
                    leitor = PdfReader(f)
                    texto = "".join([page.extract_text() or '' for page in leitor.pages])
                cnpjs = self.encontrar_cnpjs_nf(texto)
                if cnpjs:
                    cnpj_limpo = self.limpar_cnpj(cnpjs[0])
                    pasta_destino = os.path.join(destino, cnpj_limpo)
                    self.criar_diretorio(pasta_destino)
                    shutil.copy2(caminho_completo, os.path.join(pasta_destino, arquivo))
                else:
                    shutil.copy2(caminho_completo, os.path.join(destino_sem_cnpj, arquivo))
            except Exception as e:
                print(f"\nErro ao processar {arquivo}: {e}")

    def mesclar_pastas(self) -> None:
        caminho_boletos = os.path.join(self.organizados_dir, 'Boletos_organizados')
        caminho_nfs = os.path.join(self.organizados_dir, 'nfs_organizados')
        caminho_destino = os.path.join(self.organizados_dir, 'Pastas_Mescladas')
        if not os.path.exists(caminho_boletos) or not os.path.exists(caminho_nfs):
            print("\nErro: Pastas de boletos ou NF-es organizadas não encontradas.")
            return
        self.criar_diretorio(caminho_destino)

        caminho_sem_cnpj = os.path.join(caminho_nfs, 'nfs sem cnpj')
        if os.path.exists(caminho_sem_cnpj):
            destino_sem_cnpj = os.path.join(caminho_destino, 'nfs sem cnpj')
            if os.path.exists(destino_sem_cnpj):
                shutil.rmtree(destino_sem_cnpj)
            shutil.copytree(caminho_sem_cnpj, destino_sem_cnpj)
            print("\nPasta 'nfs sem cnpj' copiada para destino.")

        pastas_boletos = set(os.listdir(caminho_boletos))
        pastas_nfs = set(os.listdir(caminho_nfs)) - {'nfs sem cnpj'}
        pastas_comuns = pastas_boletos & pastas_nfs
        if not pastas_comuns:
            print("\nNenhuma pasta com CNPJ correspondente encontrada.")
            return

        print(f"\nMesclando {len(pastas_comuns)} pastas com CNPJ correspondente...")
        for pasta in tqdm(pastas_comuns, desc='Mesclando pastas'):
            pasta_destino = os.path.join(caminho_destino, pasta)
            self.criar_diretorio(pasta_destino)
            for origem in [os.path.join(caminho_boletos, pasta), os.path.join(caminho_nfs, pasta)]:
                for item in os.listdir(origem):
                    shutil.copy2(os.path.join(origem, item), pasta_destino)

    def enviar_emails(self) -> bool:
        if not self.email_credenciais['usuario'] or not self.email_credenciais['senha']:
            print("\nErro: Credenciais de email não configuradas corretamente.")
            return False

        pasta_base = os.path.join(self.organizados_dir, 'Pastas_Mescladas')
        if not os.path.exists(pasta_base):
            print(f"\nErro: Pasta base '{pasta_base}' não encontrada!")
            return False

        subpastas = [d for d in os.listdir(pasta_base) if os.path.isdir(os.path.join(pasta_base, d)) and d != 'nfs sem cnpj']
        if not subpastas:
            print("\nErro: Nenhuma subpasta encontrada na pasta base!")
            return False

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_credenciais['usuario'], self.email_credenciais['senha'])
        except Exception as e:
            print(f"\nErro ao conectar ao servidor SMTP: {e}")
            return False

        enviados = 0
        print("\nIniciando envio de emails...")

        for cnpj in tqdm(subpastas, desc="Enviando emails", unit="CNPJ"):
            if cnpj not in self.CNPJ_PARA_EMAIL or not self.CNPJ_PARA_EMAIL[cnpj]:
                print(f"\nAviso: CNPJ {cnpj} não tem e-mail definido - pulando...")
                continue
            destinatario = self.CNPJ_PARA_EMAIL[cnpj]
            pasta_cnpj = os.path.join(pasta_base, cnpj)
            arquivos = [f for f in os.listdir(pasta_cnpj) if os.path.isfile(os.path.join(pasta_cnpj, f))]
            if not arquivos:
                print(f"\nAviso: Pasta {cnpj} está vazia - pulando...")
                continue

            msg = MIMEMultipart()
            msg['From'] = self.email_credenciais['usuario']
            msg['To'] = destinatario
            msg['Subject'] = f"Boletos e Notas Fiscais - CNPJ: {cnpj}"
            corpo = f"""Prezados,

Segue em anexo os documentos referentes ao CNPJ: {cnpj}.

Atenciosamente,
Sistema Automático"""
            msg.attach(MIMEText(corpo, 'plain'))

            anexos_com_sucesso = 0
            for arquivo in arquivos:
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
                    print(f"\nErro ao anexar {arquivo}: {e}")

            if anexos_com_sucesso == 0:
                print(f"\nAviso: Nenhum arquivo válido em {cnpj} - pulando envio...")
                continue

            try:
                server.sendmail(self.email_credenciais['usuario'], destinatario, msg.as_string())
                print(f"\nEmail enviado para {destinatario} (CNPJ: {cnpj})")
                enviados += 1
            except Exception as e:
                print(f"\nFalha ao enviar email para {destinatario}: {e}")

        server.quit()
        print(f"\nTotal de emails enviados com sucesso: {enviados}")
        return enviados > 0

    def executar(self) -> None:
        print("\n=== INÍCIO DO PROCESSAMENTO ===")
        print("\n[ETAPA 1/3] Organizando boletos...")
        self.organizar_boletos()
        print("\n[ETAPA 2/3] Organizando NF-es...")
        self.organizar_nfs()
        print("\n[ETAPA 3/3] Mesclando pastas com CNPJ correspondente...")
        self.mesclar_pastas()
        print("\n[ETAPA BÔNUS] Enviando emails para CNPJs mapeados...")
        if self.CNPJ_PARA_EMAIL:
            self.enviar_emails()
        else:
            print("\nAviso: Nenhum CNPJ mapeado para envio de emails.")
        print("\n=== PROCESSAMENTO CONCLUÍDO ===")
        print(f"Resultados disponíveis em: {os.path.abspath(self.organizados_dir)}")

if __name__ == "__main__":
    gerenciador = GerenciadorDocumentos()
    gerenciador.executar()
