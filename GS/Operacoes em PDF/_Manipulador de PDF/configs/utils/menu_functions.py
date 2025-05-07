from .functions import (f01, f02, f03, f04, f05, f06, f07, f08, f09, f10,
                        f11, f12, f13, f14, f15, f16, f17, f18, f19, f20, f21,
                        N_FUNCTIONS, NAMES)
from .report_functions import salva_relatorio
from datetime import datetime
import time


def process_option(option: int) -> None:
    """
    Processa a opção do usuário.
    """
    # Data atual.
    data = datetime.now().strftime("%d/%m/%Y")

    if 0 < option <= N_FUNCTIONS:
        st = time.time()  # Tempo de início da execução.
        n_pags = eval(f'f{option:02}()')
        tipo = NAMES[option]
        exec_time = time.time() - st  # Tempo de execução.
        values = [[data, tipo, n_pags, exec_time]]  # Valores para serem salvos no relatório.
        salva_relatorio(values)


def main_hub():
    option: int = -1
    # Aguarda até que seja recebida uma opção válida.
    while option < 0 or option > N_FUNCTIONS:
        print('Digite uma opção de documento para separar.')
        print_main_msg()
        try:
            option = int(input('Escolha: '))
            limpa_terminal()
        except ValueError:
            pass
    process_option(option)


def print_main_msg() -> None:
    for key in NAMES.keys():
        print(f'{key}: {NAMES[key]}')


def limpa_terminal() -> None:
    print('\n' * 50)
