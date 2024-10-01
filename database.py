import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def connect_db():
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        f'SERVER={os.getenv("DB_SERVER")};'
        f'DATABASE={os.getenv("DB_DATABASE")};'
        f'UID={os.getenv("DB_UID")};'
        f'PWD={os.getenv("DB_PWD")}'
    )
    return conn

def search_debtors():
    """
    Busca os clientes inadimplentes no novo banco de dados com boletos pendentes ou vencidos.
    """
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        SELECT RAZAO_SOCIAL, FONE1, EMAIL, STATUS, DAT_VENCIMENTO
        FROM vw_client
        WHERE STATUS = 'A'
        AND DAT_VENCIMENTO < ?
        AND DATEDIFF(DAY, DAT_VENCIMENTO, GETDATE()) > 3
        AND DATEDIFF(DAY, DAT_VENCIMENTO, GETDATE()) <= 60;
    """
    today = datetime.today()
    cursor.execute(query, today)
    results = cursor.fetchall()
    conn.close()

    customers = [
        {
            'name': row.RAZAO_SOCIAL,
            'number': row.FONE1,
            'email': row.EMAIL,
            'due_date': row.DAT_VENCIMENTO,
            'days_late': (today - row.DAT_VENCIMENTO).days 
        }
        for row in results
    ]

    customers = [customer for customer in customers if customer['days_late'] > 3]

    return customers

def check_payment_status(name_customer=None, number_customer=None):
    """
    Verifica no banco de dados se o status do cliente foi quitado.
    :return: True se o boleto foi pago (status Q), False caso contrário
    """
    if name_customer is None or number_customer is None:
        return False

    conn = connect_db()
    cursor = conn.cursor()

    query = """
        SELECT STATUS
        FROM vw_client
        WHERE RAZAO_SOCIAL = ? AND FONE1 = ?
    """
    
    cursor.execute(query, (name_customer, number_customer))
    result = cursor.fetchone()
    conn.close()

    if result and result[0] == 'Q':
        return True
    return False