import pyodbc

def connect_db():
    conn = pyodbc.connect(
        r'DRIVER={SQL Server};'
        r'SERVER=DESKTOP-CMKE125;'
        r'DATABASE=CobrancaDB;'
        r'Trusted_Connection=yes;'
    )
    return conn

def search_debtors():
    """
    Busca os clientes inadimplentes no banco de dados com boletos pendentes ou vencidos.
    """
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        SELECT c.id, c.nome, c.telefone, b.dias_atrasados
        FROM clientes c
        JOIN boletos b ON c.id = b.id_cliente
        WHERE b.status = 'vencido'
    """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    # Convertendo os resultados para uma lista de dicionários
    customers = [
        {
            'id': row.id,
            'name': row.nome,
            'number': row.telefone,
            'days_late': row.dias_atrasados
        }
        for row in results
    ]
    return customers

def check_payment_status(name_customer=None, number_customer=None):
    """
    Verifica no banco de dados se o boleto do cliente foi pago.
    :return: True se o boleto foi pago, False caso contrário
    """
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