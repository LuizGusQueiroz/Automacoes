import os
import shutil

def funcao_principal():
    copiar_boletos()

def copiar_boletos():
    RED = '\033[91m'
    GREEN = '\033[92m'
    RESET = '\033[0m'
    
    pasta_destino = 'boletos_nfs'
    pastas_origem = ['apenas_boletos', 'apenas_nfs']
    
    # Criar pasta destino se não existir
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino, exist_ok=True)
    
    def copiar_arquivo_seguro(origem, destino):
        """Copia um arquivo com tratamento de erros para caminhos longos"""
        try:
            # Verifica se o diretório de destino existe
            dir_destino = os.path.dirname(destino)
            if not os.path.exists(dir_destino):
                os.makedirs(dir_destino, exist_ok=True)
            
            # Tenta copiar com caminho longo se necessário
            try:
                shutil.copy2(origem, destino)
            except OSError:
                # Se falhar, tenta com prefixo para caminhos longos
                origem_long = f"\\\\?\\{os.path.abspath(origem)}"
                destino_long = f"\\\\?\\{os.path.abspath(destino)}"
                shutil.copy2(origem_long, destino_long)
            
            print(f"{GREEN}✓ {os.path.basename(origem)}{RESET}")
            return True
        except Exception as e:
            print(f"{RED}✗ Falha ao copiar {os.path.basename(origem)}: {e}{RESET}")
            return False

    for origem in pastas_origem:
        print(f"\nCopiando pasta: {origem}")
        destino_final = os.path.join(pasta_destino, os.path.basename(origem))
        
        # Contadores para relatório
        sucessos = 0
        falhas = 0
        
        # Cria a estrutura de pastas primeiro
        for root, dirs, _ in os.walk(origem):
            for dir_name in dirs:
                dir_origem = os.path.join(root, dir_name)
                dir_destino = os.path.join(pasta_destino, os.path.basename(origem), 
                                         os.path.relpath(dir_origem, origem))
                
                try:
                    os.makedirs(dir_destino, exist_ok=True)
                except Exception as e:
                    print(f"{RED}✗ Falha ao criar pasta {dir_name}: {e}{RESET}")
                    falhas += 1
        
        # Copia os arquivos um por um
        for root, _, files in os.walk(origem):
            for file in files:
                origem_completo = os.path.join(root, file)
                destino_completo = os.path.join(pasta_destino, os.path.basename(origem), 
                                             os.path.relpath(root, origem), file)
                
                if copiar_arquivo_seguro(origem_completo, destino_completo):
                    sucessos += 1
                else:
                    falhas += 1
        
        print(f"\nResumo para {origem}:")
        print(f"{GREEN}Arquivos copiados com sucesso: {sucessos}{RESET}")
        print(f"{RED}Arquivos com falha: {falhas}{RESET}")

funcao_principal()