import os
import shutil
from tqdm import tqdm  

def funcao_principal():
    pasta_destino = 'apenas_boletos'
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)  

    processar_boletos(pasta_destino)

def processar_boletos(pasta_destino):
    dir = 'BOLETOS'
    if not os.path.exists(dir):
        print(f'Diretório {dir} não encontrado')
        return
    
    nome_arquivos = [f for f in os.listdir(dir) if f.lower().endswith('.pdf')]
    print(f"Total de PDFs encontrados: {len(nome_arquivos)}")

    for nome_arquivo in tqdm(nome_arquivos, desc="Processando boletos"):
        try:
            nome_original = nome_arquivo
            print(f"\nProcessando: {nome_original}") 

            nome_tratado = nome_original.replace('_', ' ').replace('-', ' ').strip()
            if not nome_tratado:
                nome_tratado = 'Sem Nome'
                print("Aviso: Nome vazio após tratamento")

            pasta_processada = os.path.join(pasta_destino, nome_tratado)
            
            origem = os.path.join(dir, nome_original)
            if not os.path.exists(origem):
                print(f"Erro: Arquivo não encontrado - {origem}")
                continue

            if not os.path.exists(pasta_processada):
                os.makedirs(pasta_processada)
                print(f"Criada pasta: {pasta_processada}")

            destino = os.path.join(pasta_processada, nome_original)
            shutil.copy(origem, destino)
            print(f'Copiado: {origem} -> {destino}')

        except Exception as e:
            print(f'Erro crítico ao processar {nome_original}: {str(e)}')
            continue
        
        remover_pasta_se_vazia(pasta_processada)
def pasta_vazia(pasta):
    """Verifica se uma pasta está vazia"""
    if not os.path.exists(pasta):
        return True
    return not os.listdir(pasta)



def remover_pasta_se_vazia(caminho_pasta):
    """Remove a pasta se estiver vazia, incluindo subpastas vazias"""
    try:
        if os.path.exists(caminho_pasta):
            if not os.listdir(caminho_pasta):
                os.rmdir(caminho_pasta)
                print(f'Pasta vazia removida: {caminho_pasta}')
                return True
        return False
    except Exception as e:
        print(f'Erro ao verificar/remover pasta {caminho_pasta}: {str(e)}')
        return False

def processar_boletos(pasta_destino):
    dir = 'BOLETOS'
    if not os.path.exists(dir):
        print(f'Diretório {dir} não encontrado')
        return
    
    nome_arquivos = [f for f in os.listdir(dir) if f.lower().endswith('.pdf')]
    
    for nome_arquivo in tqdm(nome_arquivos, desc="Processando boletos"):
        try:
            nome_original = nome_arquivo
            nome_tratado = nome_original.replace(' ', '_')
            partes = nome_tratado.split("-")
            nome_tratado = '_'.join(partes[1:-1]).strip() if len(partes) > 1 else nome_tratado.strip()
            nome_tratado = nome_tratado if nome_tratado else 'Sem Nome'

            pasta_processada = os.path.join(pasta_destino, nome_tratado)
            os.makedirs(pasta_processada, exist_ok=True)

            origem = os.path.join(dir, nome_original)
            destino = os.path.join(pasta_processada, nome_original)

            shutil.copy(origem, destino)
            print(f'Copiado: {origem} -> {destino}')
            
        except Exception as e:
            print(f'Erro ao processar {nome_original}: {str(e)}')
        
        finally:
            remover_pasta_se_vazia(pasta_processada)

def funcao_principal():
    pasta_destino = 'apenas_boletos'
    os.makedirs(pasta_destino, exist_ok=True)
    processar_boletos(pasta_destino)
    
    for root, dirs, files in os.walk(pasta_destino, topdown=False):
        for dir in dirs:
            remover_pasta_se_vazia(os.path.join(root, dir))

if __name__ == "__main__":
    funcao_principal()