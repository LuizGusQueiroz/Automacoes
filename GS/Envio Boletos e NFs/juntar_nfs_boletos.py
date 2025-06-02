import os
import shutil
from tqdm import tqdm

def comparar_e_copiar_pastas():
    # Definindo os caminhos
    caminho_boletos = os.path.join('arquivos_organizados', 'Boletos_organizados')
    caminho_nfs = os.path.join('arquivos_organizados', 'nfs_organizados')
    caminho_destino = os.path.join('arquivos_organizados', 'Pastas_Mescladas')
    caminho_sem_cnpj = os.path.join('arquivos_organizados', 'nfs_organizados', 'nfs sem cnpj')
    
    # Verificando se as pastas existem
    if not os.path.exists(caminho_boletos):
        print(f"Erro: Pasta não encontrada - {caminho_boletos}")
        return
    if not os.path.exists(caminho_nfs):
        print(f"Erro: Pasta não encontrada - {caminho_nfs}")
        return
    
    # Criando pasta de destino
    os.makedirs(caminho_destino, exist_ok=True)
    
    # 1. Copiar pasta 'nfs sem cnpj' se existir
    if os.path.exists(caminho_sem_cnpj):
        destino_sem_cnpj = os.path.join(caminho_destino, 'nfs sem cnpj')
        print("\nCopiando pasta 'nfs sem cnpj'...")
        
        if os.path.exists(destino_sem_cnpj):
            shutil.rmtree(destino_sem_cnpj)
            
        shutil.copytree(caminho_sem_cnpj, destino_sem_cnpj)
        print(f"Pasta 'nfs sem cnpj' copiada para {destino_sem_cnpj}")
    else:
        print("\nAviso: Pasta 'nfs sem cnpj' não encontrada")
    
    # 2. Processar pastas com nomes correspondentes
    pastas_boletos = [p for p in os.listdir(caminho_boletos) if os.path.isdir(os.path.join(caminho_boletos, p))]
    pastas_nfs = [p for p in os.listdir(caminho_nfs) if os.path.isdir(os.path.join(caminho_nfs, p))]
    
    pastas_comuns = set(pastas_boletos) & set(pastas_nfs)
    
    if not pastas_comuns:
        print("\nNenhuma pasta com nome correspondente encontrada.")
        return
    
    print(f"\nEncontradas {len(pastas_comuns)} pastas com nomes correspondentes:")
    
    for pasta in tqdm(pastas_comuns, desc="Mesclando pastas"):
        pasta_destino = os.path.join(caminho_destino, pasta)
        os.makedirs(pasta_destino, exist_ok=True)
        
        # Copiar conteúdo dos boletos
        origem_boletos = os.path.join(caminho_boletos, pasta)
        for item in os.listdir(origem_boletos):
            src = os.path.join(origem_boletos, item)
            dst = os.path.join(pasta_destino, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        
        # Copiar conteúdo das NFs
        origem_nfs = os.path.join(caminho_nfs, pasta)
        for item in os.listdir(origem_nfs):
            src = os.path.join(origem_nfs, item)
            dst = os.path.join(pasta_destino, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
    
    print(f"\nProcesso concluído! Resultados em: {caminho_destino}")

if __name__ == "__main__":
    comparar_e_copiar_pastas()