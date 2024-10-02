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
    Busca os clientes inadimplentes e agrupa por nome/número, consolidando os boletos em aberto.
    """
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        SELECT RAZAO_SOCIAL, FONE1, EMAIL, STATUS, DAT_VENCIMENTO
        FROM vw_client
        WHERE STATUS = 'A'
        AND DAT_VENCIMENTO < ?
        AND DATEDIFF(DAY, DAT_VENCIMENTO, GETDATE()) > 3
        AND DATEDIFF(DAY, DAT_VENCIMENTO, GETDATE()) <= 20;
    """
    today = datetime.today()
    cursor.execute(query, today)
    results = cursor.fetchall()
    conn.close()

    # Dicionário para agrupar boletos por cliente
    customers_dict = {}

    for row in results:
        name = row.RAZAO_SOCIAL
        number = row.FONE1
        days_late = (today - row.DAT_VENCIMENTO).days
        email = row.EMAIL

        if (name, number) not in customers_dict:
            customers_dict[(name, number)] = {
                'name': name,
                'number': number,
                'email': email,
                'boletos': 0,
                'total_days_late': 0,
            }

        customers_dict[(name, number)]['boletos'] += 1
        customers_dict[(name, number)]['total_days_late'] += days_late

    customers = [
        {
            'name': customer['name'],
            'number': customer['number'],
            'email': customer['email'],
            'boletos': customer['boletos'],
            'total_days_late': customer['total_days_late'],
        }
        for customer in customers_dict.values()
    ]

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