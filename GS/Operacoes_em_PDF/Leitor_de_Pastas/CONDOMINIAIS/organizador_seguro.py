import os
import shutil
from difflib import SequenceMatcher
from tqdm import tqdm

def similar(a, b, threshold=1.0):
    """Verifica se duas strings são similares com um limiar mínimo"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold

def encontrar_pasta_correspondente(nome_empresa, pastas_existentes):
    """Encontra a pasta mais similar para o arquivo"""
    for pasta in pastas_existentes:
        if similar(nome_empresa, pasta):
            return pasta
    return None

def extrair_nome_empresa(nome_arquivo):
    """Extrai o nome da empresa do nome do arquivo"""
    try:
        nome = os.path.splitext(nome_arquivo)[0]
        partes = [p for p in nome.replace('-', ' ').replace('_', ' ').split() if not p.isdigit()]
        if len(partes) > 2:
            return ' '.join(partes[1:-1]).strip()
        return ' '.join(partes).strip() or "SEM_NOME"
    except Exception:
        return "SEM_NOME"

def criar_pasta_segura(caminho):
    """Cria uma pasta com tratamento de erros"""
    try:
        os.makedirs(caminho, exist_ok=True)
        return True
    except Exception as e:
        print(f"\nErro ao criar pasta {caminho}: {str(e)}")
        return False

def copiar_arquivo_seguro(origem, destino):
    """Copia arquivos com tratamento robusto de erros"""
    try:
        dir_destino = os.path.dirname(destino)
        if not criar_pasta_segura(dir_destino):
            return False
        
        shutil.copy2(origem, destino)
        return True
    except Exception as e:
        print(f"\nErro ao copiar {origem} para {destino}: {str(e)}")
        return False

def processar_pasta(pasta_origem, prefixo, dir_destino, pastas_empresas):
    """Processa uma pasta de documentos"""
    if not os.path.exists(pasta_origem):
        print(f"\nAviso: Pasta {pasta_origem} não encontrada!")
        return pastas_empresas
    
    arquivos = [f for f in os.listdir(pasta_origem) if f.lower().endswith('.pdf')]
    if not arquivos:
        print(f"\nAviso: Nenhum PDF encontrado em {pasta_origem}")
        return pastas_empresas
    
    for arquivo in tqdm(arquivos, desc=f"Processando {os.path.basename(pasta_origem)}"):
        try:
            nome_empresa = extrair_nome_empresa(arquivo)
            origem = os.path.join(pasta_origem, arquivo)
            
            if not os.path.exists(origem):
                print(f"\nAviso: Arquivo não encontrado - {origem}")
                continue
                
            pasta_destino = encontrar_pasta_correspondente(nome_empresa, pastas_empresas) or nome_empresa
            destino = os.path.join(dir_destino, pasta_destino, f"{prefixo}_{arquivo}")
            
            if copiar_arquivo_seguro(origem, destino) and pasta_destino not in pastas_empresas:
                pastas_empresas.append(pasta_destino)
                
        except Exception as e:
            print(f"\nErro ao processar {arquivo}: {str(e)}")
    
    return pastas_empresas

def processar_e_agrupar_arquivos():
    """Função principal que orquestra o processamento"""
    dir_boletos = os.path.abspath("BOLETOS")
    dir_notas = os.path.abspath("NOTA_FISCAL")
    dir_destino = os.path.abspath("DOCUMENTOS_ORGANIZADOS")
    
    print("\nIniciando organização de documentos...")
    print(f"Origem Boletos: {dir_boletos}")
    print(f"Origem Notas: {dir_notas}")
    print(f"Destino: {dir_destino}\n")
    
    pastas_empresas = []
    pastas_empresas = processar_pasta(dir_boletos, "BOLETO", dir_destino, pastas_empresas)
    pastas_empresas = processar_pasta(dir_notas, "NOTA", dir_destino, pastas_empresas)
    
    print("\nOrganização concluída!")
    print(f"Total de empresas identificadas: {len(pastas_empresas)}")
    print(f"Documentos organizados em: {dir_destino}")

if __name__ == "__main__":
    processar_e_agrupar_arquivos()