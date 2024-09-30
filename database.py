import pyodbc
from datetime import datetime

def connect_db():
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=BDINFARMA-2019;'
        'DATABASE=DMD;'
        'UID=SA;'
        'PWD=AGzzcso1$'
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

    # Convertendo os resultados para uma lista de dicionários
    customers = [
        {
            'name': row.RAZAO_SOCIAL,
            'number': row.FONE1,
            'email': row.EMAIL,
            'due_date': row.DAT_VENCIMENTO,
            'days_late': (today - row.DAT_VENCIMENTO).days  # Cálculo dos dias de atraso
        }
        for row in results
    ]

    # Filtrando apenas os clientes que estão atrasados há mais de 3 dias
    customers = [customer for customer in customers if customer['days_late'] > 3]

    return customers

def check_payment_status(name_customer=None, number_customer=None):
    """
    Verifica no banco de dados se o status do cliente foi quitado.
    :return: True se o boleto foi pago (status Q), False caso contrário
    """
    if name_customer is None or number_customer is None:
        return False  # Retorna False se não houver informações do cliente

    conn = connect_db()
    cursor = conn.cursor()

    # Query que verifica diretamente o status do cliente
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
