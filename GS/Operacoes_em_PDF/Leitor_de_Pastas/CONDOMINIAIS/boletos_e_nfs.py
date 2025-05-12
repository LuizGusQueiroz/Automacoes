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
    import os
import shutil
from difflib import SequenceMatcher

def funcao_principal():
    processar_boletos()
    return

def verificar_nomes_iguais(nomes_tratados):
    contagem_nomes = {}
    
    for nome in nomes_tratados:
        if nome in contagem_nomes:
            contagem_nomes[nome] += 1
        else:
            contagem_nomes[nome] = 1
    
    nomes_repetidos = {nome: count for nome, count in contagem_nomes.items() if count > 1}
    
    return nomes_repetidos

def processar_boletos():
    dir = "BOLETOS"
    if not os.path.exists(dir):
        print(f"Diretório {dir} não encontrado!")
        return
    
    nome_arquivos = os.listdir(dir)
    nomes_tratados = []
    mapeamento_nomes = {}  
    for nome_arquivo in nome_arquivos:
        nome_tratado = nome_arquivo.replace('-', '').split()
        nome_tratado = ' '.join(nome_tratado[0:-1])
        
        nomes_tratados.append(nome_tratado)
        
        if nome_tratado not in mapeamento_nomes:
            mapeamento_nomes[nome_tratado] = []
        mapeamento_nomes[nome_tratado].append(nome_arquivo)
        
        print(nome_tratado)

    nomes_repetidos = verificar_nomes_iguais(nomes_tratados)
    
    if nomes_repetidos:
        print("\nNomes repetidos encontrados:")
        for nome, count in nomes_repetidos.items():
            print(f"{nome} ({count} ocorrências)")
            print("Arquivos correspondentes:")
            for arquivo in mapeamento_nomes[nome]:
                print(f"  - {arquivo}")
    else:
        print("\nNenhum nome repetido encontrado.")

def similar(a, b, threshold=0.9):
    """Verifica se duas strings são similares com um limiar mínimo"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold

def encontrar_pasta_correspondente(nome_pdf, pastas_existentes):
    """Encontra a pasta mais similar para o PDF"""
    for pasta in pastas_existentes:
        if similar(nome_pdf, pasta):
            return pasta
    return None

def distribuir_pdfs():
    dir_pdf = "NOTA_FISCAL"
    dir_pastas = "apenas_nfs"
    
    if not os.path.exists(dir_pdf):
        print(f"Erro: Diretório {dir_pdf} não encontrado!")
        return
    
    if not os.path.exists(dir_pastas):
        os.makedirs(dir_pastas)
        print(f"Diretório {dir_pastas} criado")

    pdfs = [f for f in os.listdir(dir_pdf) if f.lower().endswith('.pdf')]
    pastas_existentes = [d for d in os.listdir(dir_pastas) if os.path.isdir(os.path.join(dir_pastas, d))]
    
    for pdf in pdfs:
        nome_base = ' '.join(pdf.split()[:-1]).replace('.pdf', '').strip()
        
        
        pasta_destino = encontrar_pasta_correspondente(nome_base, pastas_existentes)
        
        if pasta_destino:
            destino = os.path.join(dir_pastas, pasta_destino, pdf)
            origem = os.path.join(dir_pdf, pdf)
            shutil.copy(origem, destino)
            print(f"Copiado {pdf} para pasta existente: {pasta_destino}")
        else:
            nova_pasta = os.path.join(dir_pastas, nome_base)
            os.makedirs(nova_pasta, exist_ok=True)
            destino = os.path.join(nova_pasta, pdf)
            origem = os.path.join(dir_pdf, pdf)
            shutil.copy(origem, destino)
            print(f"Criada nova pasta {nome_base} para o arquivo {pdf}")
            pastas_existentes.append(nome_base) 
    print("\nProcesso concluído!")

distribuir_pdfs()