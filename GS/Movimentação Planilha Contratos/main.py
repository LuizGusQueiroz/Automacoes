import shutil
import os


def main() -> None:

    path = '..'
    while 'OneDrive' not in os.listdir(path):
        path += '/..'
    path += '/OneDrive - KMF - CONSULTORIA EMPRESARIAL E TREINAMENTOS LTDA - ME'
    origem = path + '/Controladoria/Dados - T.I/Histórico de Contratos .xlsx'
    destino = path + '/Movimentações de Lotação/Histórico de Contratos .xlsx'

    try:  # Copia o arquivo de origem para destino, substituindo o atual arqiuivo em destino.
        shutil.copy2(origem, destino)
        print('Sucesso!')
    except FileNotFoundError:
        print('Arquivo não encontrado')
    except Exception as e:
        print(e)
    finally:
        input()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
