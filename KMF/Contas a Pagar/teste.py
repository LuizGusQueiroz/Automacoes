from PyPDF2 import PdfReader
import os
from tqdm import tqdm
from typing import Dict
from PyPDF2.errors import PdfReadError
import pandas as pd
import pikepdf


def get_rows(path: str):
    try:
        with open(path, 'rb') as file:
            rows = PdfReader(file).pages[0].extract_text().split('\n')
            return rows
    except FileNotFoundError:
        if not path.startswith('Y:\\'):
            return None
        new_path = path.replace('Y:\\CELULA FISCAL - FORTES', 'Z:')
        if new_path != path:
            return get_rows(new_path)
        return None
    except (PdfReadError, TypeError, KeyError, IndexError):
        return None

d = {}
rows = None
df = pd.read_excel('t.xlsx')
for path in tqdm(df['path']):
    rows = get_rows(path)
    if rows is None:
        continue
    row = rows[0]


    if row in d:
        d[row] += 1
    else:
        d[row] = 1

print('\n')
for i in d:
    print([d[i], i])