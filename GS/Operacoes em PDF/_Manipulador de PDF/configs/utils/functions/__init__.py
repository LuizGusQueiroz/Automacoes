import pathlib
import os
from .f01 import f01
from .f02 import f02
from .f03 import f03
from .f04 import f04
from .f05 import f05
from .f06 import f06
from .f07 import f07
from .f08 import f08
from .f09 import f09
from .f10 import f10
from .f11 import f11
from .f12 import f12
from .f13 import f13
from .f14 import f14
from .f15 import f15
from .f16 import f16
from .f17 import f17
from .f18 import f18
from .f19 import f19
from .f20 import f20
from .f21 import f21

# Caminho do diretório onde este __init__.py está.
diretorio = pathlib.Path(__file__).parent
# Conta quantos arquivos de função existem no diretório.
N_FUNCTIONS = len([file for file in os.listdir(diretorio) if file.startswith('f') and file.endswith('.py')])
__all__ = [f'f{i:02}' for i in range(1, N_FUNCTIONS+1)]
# Nomeia cada função ao seu nome de arquivo.
NAMES = {
    1: 'Documentos de Admissão',
    2: 'Documentos de Rescisão',
    3: 'Boletos BMP',
    4: 'Boletos de Cobrança',
    5: 'Fichas de Registro',
    6: 'Folha de Pagamento, Férias e Rescisão',
    7: 're FGTS',
    8: 'Listagem de Conferência',
    9: 'Recibos de Pagamento Fortes',
    10: 'Recibos FOLK',
    11: 'Relatório de Serviços Administrativos',
    12: 'Resumo Geral Mês/Período',
    13: 'NFs Fortaleza',
    14: 'Demonstrativo de Férias',
    15: 'NFs Eusébio',
    16: 'Cartas Singular',
    17: 'Rendimentos Protheus',
    18: 'Rendimentos Fortes',
    19: 'Planos de Saúde',
    20: 'Folha por Centro de Custo Protheus',
    21: 'Recibos de Pagamento Protheus'
}
