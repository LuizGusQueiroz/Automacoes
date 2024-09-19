import pyodbc
import json
from typing import Dict, Tuple



def main() -> None:
    params = get_params('creds.json')
    # Cria uma string necessária para a conexão.
    conn_str = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={params['server']};DATABASE={params['database']};UID={params['username']};PWD={params['password']};TrustServerCertificate=yes;'
    # Inicializa a conexão.
    conn, cursor = start_conn(conn_str)
    # Execute uma consulta
    cursor.execute('SELECT CODIGO FROM EST')

    # Iterando sobre os resultados
    for row in cursor:
        print(row)

    end_conn(conn, cursor)


def get_params(path: str) -> Dict[str, str]:
    # Lê os parâmetros da conexão de um json e retorna como Dict.
    with open(path, 'r', encoding='utf-8') as file:
        params: Dict = json.load(file)
    return params


def start_conn(conn_str: str) -> Tuple[pyodbc.Connection, pyodbc.Cursor] | None:
    # Estabelece a conexão.
    # É necessário ter o OBDC instalado.
    # Caso não esteja, baixar em: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16#download-for-windows
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        return conn, cursor
    except pyodbc.Error as e:
        print(f"Erro ao conectar: {e}")


def end_conn(conn: pyodbc.Connection, cursor: pyodbc.Cursor) -> None:
    # Feche a conexão
    cursor.close()
    conn.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
