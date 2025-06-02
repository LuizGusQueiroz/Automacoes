import os
import re
import shutil
from PyPDF2 import PdfReader
from tqdm import tqdm
from typing import List, Optional

class GerenciadorDocumentos:
    def __init__(self):
        # Configuração de caminhos
        self.base_dir = 'CONDOMINIAIS'
        self.boletos_dir = os.path.join(self.base_dir, 'BOLETOS')
        self.nfs_dir = os.path.join(self.base_dir, 'NOTA FISCAL')
        self.organizados_dir = 'arquivos_organizados'
        
        # Padrões de CNPJ
        self.CNPJ_PATTERN = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'
        self.CNPJ_IGNORADO = "16.707.848/0001-95"

    def criar_diretorio(self, caminho: str) -> None:
        """Cria diretório se não existir"""
        os.makedirs(caminho, exist_ok=True)

    def limpar_cnpj(self, cnpj: str) -> str:
        """Remove caracteres não numéricos do CNPJ"""
        return re.sub(r'\D', '', cnpj)

    def extrair_texto_pdf(self, caminho_pdf: str) -> List[str]:
        """Extrai texto da primeira página do PDF"""
        if not os.path.exists(caminho_pdf):
            return []
        
        with open(caminho_pdf, 'rb') as arquivo:
            leitor = PdfReader(arquivo)
            primeira_pagina = leitor.pages[0]
            return primeira_pagina.extract_text().split('\n')

    def encontrar_cnpj_boleto(self, linhas_texto: List[str]) -> Optional[str]:
        """Encontra CNPJ no texto do boleto (prioriza o segundo CNPJ encontrado)"""
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
        """Encontra todos os CNPJs em uma NF-e"""
        cnpjs = re.findall(self.CNPJ_PATTERN, texto)
        return [c for c in cnpjs if c != self.CNPJ_IGNORADO]

    def organizar_boletos(self) -> None:
        """Organiza boletos por CNPJ"""
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
        """Organiza NF-es por CNPJ"""
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
                    shutil.move(caminho_completo, os.path.join(pasta_destino, arquivo))
                else:
                    shutil.move(caminho_completo, os.path.join(destino_sem_cnpj, arquivo))
                    
            except Exception as e:
                print(f"\nErro ao processar {arquivo}: {e}")

    def mesclar_pastas(self) -> None:
        """Mescla pastas de boletos e NF-es com mesmo CNPJ"""
        caminho_boletos = os.path.join(self.organizados_dir, 'Boletos_organizados')
        caminho_nfs = os.path.join(self.organizados_dir, 'nfs_organizados')
        caminho_destino = os.path.join(self.organizados_dir, 'Pastas_Mescladas')
        
        if not os.path.exists(caminho_boletos) or not os.path.exists(caminho_nfs):
            print("\nErro: Pastas de boletos ou NF-es organizadas não encontradas.")
            return
        
        self.criar_diretorio(caminho_destino)
        
        # Copiar pasta 'nfs sem cnpj' se existir
        caminho_sem_cnpj = os.path.join(caminho_nfs, 'nfs sem cnpj')
        if os.path.exists(caminho_sem_cnpj):
            destino_sem_cnpj = os.path.join(caminho_destino, 'nfs sem cnpj')
            if os.path.exists(destino_sem_cnpj):
                shutil.rmtree(destino_sem_cnpj)
            shutil.copytree(caminho_sem_cnpj, destino_sem_cnpj)
            print("\nPasta 'nfs sem cnpj' copiada para destino.")
        
        # Mesclar pastas com mesmo CNPJ
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
            
            # Copiar boletos
            origem = os.path.join(caminho_boletos, pasta)
            for item in os.listdir(origem):
                src = os.path.join(origem, item)
                shutil.copy2(src, pasta_destino)
            
            # Copiar NF-es
            origem = os.path.join(caminho_nfs, pasta)
            for item in os.listdir(origem):
                src = os.path.join(origem, item)
                shutil.copy2(src, pasta_destino)

    def executar(self) -> None:
        """Executa todo o fluxo de organização"""
        print("\n=== INÍCIO DO PROCESSAMENTO ===")
        
        # 1. Organizar boletos
        print("\n[ETAPA 1/3] Organizando boletos...")
        self.organizar_boletos()
        
        # 2. Organizar NF-es
        print("\n[ETAPA 2/3] Organizando NF-es...")
        self.organizar_nfs()
        
        # 3. Mesclar pastas
        print("\n[ETAPA 3/3] Mesclando pastas com CNPJ correspondente...")
        self.mesclar_pastas()
        
        print("\n=== PROCESSAMENTO CONCLUÍDO ===")
        print(f"Resultados disponíveis em: {os.path.abspath(self.organizados_dir)}")

if __name__ == "__main__":
    gerenciador = GerenciadorDocumentos()
    gerenciador.executar()