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