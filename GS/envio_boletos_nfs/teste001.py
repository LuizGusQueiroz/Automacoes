import os
from typing import List
import pandas as pd

def enviar_emails():

    df = pd.read_excel("usuario_senha.xlsx")
    df['cnpj ']=df['cnpj '].apply(lambda x: f"{x:014}")
    

    cnpjs:List[str] = os.listdir()



    cnpjs = cnpjs[0:-1]
    for cnpj in cnpjs:
        print(cnpj)



enviar_emails()