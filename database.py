import pyodbc
import os
from dotenv import load_dotenv

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
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        SELECT c.id, c.nome, c.telefone, b.dias_atrasados, c.email
        FROM clientes c
        JOIN boletos b ON c.id = b.id_cliente
        WHERE b.status = 'vencido'
    """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    customers = [
        {
            'id': row.id,
            'name': row.nome,
            'number': row.telefone,
            'days_late': row.dias_atrasados,
            'email': row.email
        }
        for row in results
    ]
    return customers

def check_payment_status(name_customer=None, number_customer=None):
    conn = connect_db()
    cursor = conn.cursor()

    query = """
        SELECT b.status
        FROM clientes c
        JOIN boletos b ON c.id = b.id_cliente
        WHERE b.status = 'pago'
    """
    
    conditions = []
    if name_customer:
        conditions.append("c.nome = ?")
    if number_customer:
        conditions.append("c.telefone = ?")
    
    if conditions:
        query += " AND (" + " OR ".join(conditions) + ")"

    parameters = [param for param in (name_customer, number_customer) if param]
    cursor.execute(query, parameters)
    
    result = cursor.fetchone()
    conn.close()

    if result and result[0] == 'pago':
        return True
    return False
