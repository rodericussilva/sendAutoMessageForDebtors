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
        SELECT
	        cl.Codigo,
	        cl.Razao_Social,
	        cl.Fone1,
	        cl.Email,
	        ct.Status,
	        ct.Dat_Emissao,
	        ct.Dat_Vencimento,
	        ct.Vlr_Documento
        FROM CLIEN AS cl
        JOIN CTREC AS ct
	        ON cl.Codigo = ct.Cod_Cliente
		JOIN ENXES AS en 
            ON ct.Cod_Cliente = en.Cod_Client and cod_regtri = '23' and cod_agente = '4'
        WHERE ct.Status = 'A'
        AND ct.Dat_Vencimento < ?
        AND DATEDIFF(DAY, ct.Dat_Vencimento, GETDATE()) > 3
        AND DATEDIFF(DAY, ct.Dat_Vencimento, GETDATE()) <= 20
        GROUP BY
	        cl.Codigo,
	        cl.Razao_Social,
	        cl.Fone1,
	        cl.Email,
	        ct.Status,
	        ct.Dat_Emissao,
	        ct.Dat_Vencimento,
	        ct.Vlr_Documento;
    """
    today = datetime.today()
    cursor.execute(query, today)
    results = cursor.fetchall()
    conn.close()

    customers_dict = {}

    for row in results:
        name = row.Razao_Social
        number = row.Fone1
        days_late = (today - row.Dat_Vencimento).days
        email = row.Email
        document_value = row.Vlr_Documento

        if (name, number) not in customers_dict:
            customers_dict[(name, number)] = {
                'name': name,
                'number': number,
                'email': email,
                'boletos': 0,
                'total_days_late': 0,
                'value': 0,
            }

        customers_dict[(name, number)]['boletos'] += 1

        if days_late > customers_dict[(name, number)]['total_days_late']:
            customers_dict[(name, number)]['total_days_late'] = days_late
            customers_dict[(name, number)]['value'] = document_value

    customers = [
        {
            'name': customer['name'],
            'number': customer['number'],
            'email': customer['email'],
            'boletos': customer['boletos'],
            'total_days_late': customer['total_days_late'],
            'value': customer['value']
        }
        for customer in customers_dict.values()
    ]

    return customers
    
def check_payment_status(name_customer=None, number_customer=None):
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

def get_due_date_reminders():
    conn = connect_db()
    cursor = conn.cursor()
    
    query = """
        SELECT
            cl.Razao_Social,
            cl.Fone1,
            cl.Email,
            ct.Dat_Vencimento,
            ct.Vlr_Documento
        FROM CLIEN AS cl
        JOIN CTREC AS ct 
            ON cl.Codigo = ct.Cod_Cliente
        JOIN ENXES AS en 
            ON ct.Cod_Cliente = en.Cod_Client and cod_regtri = '23' and cod_agente = '4'
        WHERE ct.Status = 'A'
          AND DATEDIFF(DAY, GETDATE(), ct.Dat_Vencimento) = 5;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    reminders_dict = {}

    for row in results:
        name = row.Razao_Social
        number = row.Fone1
        email = row.Email
        due_date = row.Dat_Vencimento
        document_value = row.Vlr_Documento

        if (name, number) not in reminders_dict:
            reminders_dict[(name, number)] = {
                'name': name,
                'number': number,
                'email': email,
                'due_date': due_date,
                'value': document_value,
                'boletos': 0,
            }

        reminders_dict[(name, number)]['boletos'] += 1

    reminders = [
        {
            'name': reminder['name'],
            'number': reminder['number'],
            'email': reminder['email'],
            'due_date': reminder['due_date'],
            'value': reminder['value'],
            'boletos': reminder['boletos'],
        }
        for reminder in reminders_dict.values()
    ]

    return reminders
