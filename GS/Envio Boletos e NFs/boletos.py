from PyPDF2 import PdfReader
from typing import List
from tqdm import tqdm
import shutil
import os


class OrganizadorBoletos:
    def __init__(self, dir_boletos: str, dir_destino: str = 'Boletos_Organizados') -> None:
        self.dir_boletos = dir_boletos  # Diretório dos boletos
        self.dir_destino = dir_destino  # Diretório de destino organizado

    def criar_diretorio(self, caminho: str) -> None:
        """Cria o diretório se ele não existir"""
        if not os.path.exists(caminho):
            os.makedirs(caminho)

    def extrair_texto_pdf(self, caminho_pdf: str) -> List[str]:
        """
        Extrai o texto da primeira página do PDF
        :param caminho_pdf: Caminho completo do arquivo PDF
        :return: Lista de linhas do texto
        """
        if not os.path.exists(caminho_pdf):
            return []
        
        with open(caminho_pdf, 'rb') as arquivo:
            leitor = PdfReader(arquivo)
            primeira_pagina = leitor.pages[0]
            return primeira_pagina.extract_text().split('\n')

    def formatar_cnpj(self, cnpj: str) -> str:
        """Remove todos os caracteres não numéricos do CNPJ/CPF"""
        return ''.join(filter(str.isdigit, cnpj))

    def encontrar_cnpj(self, linhas_texto: List[str]) -> str:
        """
        Encontra o CNPJ no texto do boleto
        :return: O segundo CNPJ encontrado ou o primeiro se não houver segundo
        """
        cnpjs = []
        for linha in linhas_texto:
            if 'CNPJ:' in linha or 'CPF/CNPJ:' in linha:
                partes = linha.split()
                if partes:  # Verifica se a linha não está vazia
                    cnpj_bruto = partes[-1]
                    cnpj_formatado = self.formatar_cnpj(cnpj_bruto)
                    if len(cnpj_formatado) in (11, 14):  # CPF tem 11, CNPJ tem 14
                        cnpjs.append(cnpj_formatado)
        
        if len(cnpjs) >= 2:
            return cnpjs[1]  # Retorna o segundo CNPJ
        elif cnpjs:
            return cnpjs[0]  # Retorna o primeiro se não tiver segundo
        return None

    def processar_boletos(self) -> None:
        """Processa todos os boletos no diretório especificado"""
        arquivos = [f for f in os.listdir(self.dir_boletos) if f.lower().endswith('.pdf')]
        
        if not arquivos:
            print("Nenhum arquivo PDF encontrado na pasta de boletos.")
            return

        self.criar_diretorio(self.dir_destino)

        for arquivo in tqdm(arquivos, desc='Organizando Boletos'):
            caminho_completo = os.path.join(self.dir_boletos, arquivo)
            linhas = self.extrair_texto_pdf(caminho_completo)
            
            cnpj = self.encontrar_cnpj(linhas)
            
            if not cnpj:
                print(f"\nAtenção: Não foi possível identificar CNPJ no arquivo {arquivo}")
                continue
            
            # Cria pasta com o CNPJ se não existir
            pasta_cnpj = os.path.join(self.dir_destino, cnpj)
            self.criar_diretorio(pasta_cnpj)
            
            # Copia o arquivo para a pasta do CNPJ
            novo_caminho = os.path.join(pasta_cnpj, arquivo)
            shutil.copy2(caminho_completo, novo_caminho)

    def executar(self) -> None:
        """Método principal para iniciar a organização"""
        try:
            print(f"\nIniciando organização de boletos...")
            print(f"Origem: {self.dir_boletos}")
            print(f"Destino: {self.dir_destino}\n")
            
            self.processar_boletos()
            
            print("\nProcesso concluído com sucesso!")
        except Exception as e:
            print(f"\nOcorreu um erro: {str(e)}")
            input("Pressione Enter para sair...")


if __name__ == "__main__":
    # Configuração dos diretórios
    pasta_boletos = 'CONDOMINIAIS/BOLETOS'  # Altere para seu caminho
    pasta_destino = 'BOLETOS_ORGANIZADOS'   # Pasta onde serão salvos os arquivos organizados
    
    organizador = OrganizadorBoletos(pasta_boletos, pasta_destino)
    organizador.executar()