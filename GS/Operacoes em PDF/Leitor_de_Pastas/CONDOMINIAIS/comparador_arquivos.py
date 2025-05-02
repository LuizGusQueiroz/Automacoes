import os
import filecmp
from datetime import datetime

def comparar_pastas(pasta1, pasta2, detalhes=False, ignorar=[], comparar_conteudo=True):
    """
    Compara duas pastas recursivamente, incluindo subpastas.

    Args:
        pasta1 (str): Caminho da primeira pasta
        pasta2 (str): Caminho da segunda pasta
        detalhes (bool): Se True, mostra detalhes de cada diferença
        ignorar (list): Lista de nomes de arquivos/pastas para ignorar
        comparar_conteudo (bool): Se True, compara conteúdo dos arquivos

    Returns:
        dict: Dicionário com os resultados da comparação
    """
    if not os.path.exists(pasta1) or not os.path.exists(pasta2):
        raise ValueError("Uma ou ambas as pastas não existem")

    resultado = {
        'pastas_iguais': [],
        'pastas_diferentes': [],
        'pastas_apenas_na_pasta1': [],
        'pastas_apenas_na_pasta2': [],
        'arquivos_iguais': [],
        'arquivos_diferentes': [],
        'arquivos_apenas_na_pasta1': [],
        'arquivos_apenas_na_pasta2': [],
        'total_itens_pasta1': 0,
        'total_itens_pasta2': 0
    }

    def caminho_relativo(base, caminho):
        return os.path.relpath(caminho, base)

    def comparar_arquivos(arquivo1, arquivo2):
        try:
            if comparar_conteudo:
                return filecmp.cmp(arquivo1, arquivo2, shallow=False)
            else:
                return (os.path.getsize(arquivo1) == os.path.getsize(arquivo2) and
                        os.path.getmtime(arquivo1) == os.path.getmtime(arquivo2))
        except OSError:
            return False

    dcmp = filecmp.dircmp(pasta1, pasta2, ignore=ignorar)

    for nome in dcmp.common_files:
        if nome in ignorar:
            continue
            
        caminho1 = os.path.join(pasta1, nome)
        caminho2 = os.path.join(pasta2, nome)
        
        if comparar_arquivos(caminho1, caminho2):
            resultado['arquivos_iguais'].append(nome)
        else:
            diferenca = {
                'arquivo': nome,
                'tamanho_pasta1': os.path.getsize(caminho1),
                'tamanho_pasta2': os.path.getsize(caminho2),
                'modificacao_pasta1': datetime.fromtimestamp(os.path.getmtime(caminho1)),
                'modificacao_pasta2': datetime.fromtimestamp(os.path.getmtime(caminho2))
            }
            resultado['arquivos_diferentes'].append(diferenca)

    resultado['arquivos_apenas_na_pasta1'] = dcmp.left_only
    resultado['arquivos_apenas_na_pasta2'] = dcmp.right_only

    for subpasta in dcmp.common_dirs:
        if subpasta in ignorar:
            continue
            
        sub_resultado = comparar_pastas(
            os.path.join(pasta1, subpasta),
            os.path.join(pasta2, subpasta),
            detalhes=False,
            ignorar=ignorar,
            comparar_conteudo=comparar_conteudo
        )
        
        caminho_rel = caminho_relativo(pasta1, os.path.join(pasta1, subpasta))
        
        if not sub_resultado['arquivos_diferentes'] and not sub_resultado['pastas_diferentes']:
            resultado['pastas_iguais'].append(caminho_rel)
        else:
            resultado['pastas_diferentes'].append({
                'pasta': caminho_rel,
                'detalhes': sub_resultado
            })

    for subpasta in dcmp.left_only:
        if os.path.isdir(os.path.join(pasta1, subpasta)) and subpasta not in ignorar:
            resultado['pastas_apenas_na_pasta1'].append(subpasta)

    for subpasta in dcmp.right_only:
        if os.path.isdir(os.path.join(pasta2, subpasta)) and subpasta not in ignorar:
            resultado['pastas_apenas_na_pasta2'].append(subpasta)

    resultado['total_itens_pasta1'] = sum([len(files) for _, _, files in os.walk(pasta1)])
    resultado['total_itens_pasta2'] = sum([len(files) for _, _, files in os.walk(pasta2)])

    if detalhes:
        print("\n=== RESUMO DA COMPARAÇÃO ===")
        print(f"Pasta 1: {pasta1} ({resultado['total_itens_pasta1']} itens)")
        print(f"Pasta 2: {pasta2} ({resultado['total_itens_pasta2']} itens)")
        
        print("\nPastas idênticas:", len(resultado['pastas_iguais']))
        print("Pastas diferentes:", len(resultado['pastas_diferentes']))
        print(f"Pastas apenas em {pasta1}:", len(resultado['pastas_apenas_na_pasta1']))
        print(f"Pastas apenas em {pasta2}:", len(resultado['pastas_apenas_na_pasta2']))
        
        print("\nArquivos idênticos:", len(resultado['arquivos_iguais']))
        print("Arquivos diferentes:", len(resultado['arquivos_diferentes']))
        print(f"Arquivos apenas em {pasta1}:", len(resultado['arquivos_apenas_na_pasta1']))
        print(f"Arquivos apenas em {pasta2}:", len(resultado['arquivos_apenas_na_pasta2']))

        if resultado['arquivos_diferentes']:
            print("\nARQUIVOS DIFERENTES:")
            for diff in resultado['arquivos_diferentes']:
                print(f"\nArquivo: {diff['arquivo']}")
                print(f"Tamanho: {pasta1}={diff['tamanho_pasta1']} bytes | {pasta2}={diff['tamanho_pasta2']} bytes")
                print(f"Modificação: {pasta1}={diff['modificacao_pasta1']} | {pasta2}={diff['modificacao_pasta2']}")

        if resultado['pastas_diferentes']:
            print("\nSUBPASTAS COM DIFERENÇAS:")
            for diff in resultado['pastas_diferentes']:
                print(f"\nPasta: {diff['pasta']}")
                print(f"Arquivos diferentes: {len(diff['detalhes']['arquivos_diferentes'])}")
                print(f"Arquivos faltantes: {len(diff['detalhes']['arquivos_apenas_na_pasta1'] + diff['detalhes']['arquivos_apenas_na_pasta2'])}")

    return resultado

if __name__ == "__main__":
    pasta_a = "apenas_boletos"
    pasta_b = "apenas_nfs"
    
    resultado = comparar_pastas(
        pasta_a, 
        pasta_b, 
        detalhes=True,
        ignorar=[".DS_Store", "Thumbs.db"], 
        comparar_conteudo=True  
    )