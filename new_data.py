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
        FROM vw_ctrec_clientes
        WHERE STATUS = 'A'  -- A para aberto, equivalente a vencido
    """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    # Convertendo os resultados para uma lista de dicionários
    today = datetime.today()
    customers = [
        {
            'name': row.RAZAO_SOCIAL,
            'number': row.FONE1,
            'email': row.EMAIL,
            'days_late': (row.DAT_VENCIMENTO - today).days if row.DAT_VENCIMENTO else None  # Cálculo dos dias de atraso
        }
        for row in results
    ]
    return customers

def check_payment_status(name_customer=None, number_customer=None):
    """
    Verifica no banco de dados se o status do cliente foi quitado.
    :return: True se o boleto foi pago (status Q), False caso contrário
    """
    conn = connect_db()
    cursor = conn.cursor()

    query = """
        SELECT STATUS
        FROM vw_ctrec_clientes
        WHERE STATUS = 'Q'  -- Q para quitado
    """
    
    conditions = []
    if name_customer:
        conditions.append("RAZAO_SOCIAL = ?")
    if number_customer:
        conditions.append("FONE1 = ?")
    
    if conditions:
        query += " AND (" + " OR ".join(conditions) + ")"

    parameters = [param for param in (name_customer, number_customer) if param]
    cursor.execute(query, parameters)
    
    result = cursor.fetchone()
    conn.close()

    if result and result[0] == 'Q':
        return True
    return False