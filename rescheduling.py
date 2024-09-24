import json
from datetime import datetime

RESCHEDULING_FILE = 'rescheduling.json'
LAST_SENT_FILE = 'last_sent_dates.json'

def load_rescheduling():
    """
    Carrega os reagendamentos existentes de um arquivo JSON.
    """
    try:
        with open(RESCHEDULING_FILE, 'r') as file:
            data = json.load(file)
            return data.get('reagendamentos', []) if isinstance(data, dict) else []
    except FileNotFoundError:
        return []

def save_rescheduling(rescheduling):
    """
    Salva os reagendamentos no arquivo JSON.
    """
    with open(RESCHEDULING_FILE, 'w') as file:
        json.dump({"reagendamentos": rescheduling}, file, indent=4)

def check_reschedule(name=None, number=None):
    """
    Verifica se há reagendado e se deve ser ignorado até nova data.
    
    :return: True se o cliente estiver reagendado, False caso contrário
    """
    rescheduling = load_rescheduling()
    for reagendamento in rescheduling:
        if (name and reagendamento.get('name') == name) or (number and reagendamento.get('number') == number):
            new_date = datetime.strptime(reagendamento['new_date_reschedule'], '%Y-%m-%d').date()
            if new_date > datetime.now().date():
                return True
    return False

def load_last_sent_dates():
    """
    Carrega as últimas datas de envio de mensagens de um arquivo JSON.
    """
    try:
        with open(LAST_SENT_FILE, 'r') as file:
            data = json.load(file)
            return data.get('clientes', [])
    except FileNotFoundError:
        return []

def save_last_sent_dates(last_sent_data):
    """
    Salva as últimas datas de envio de mensagens no arquivo JSON.
    """
    with open(LAST_SENT_FILE, 'w') as file:
        json.dump({"clientes": last_sent_data}, file, indent=4)

def get_last_sent_date(name, number):
    """
    Retorna a última data de envio para um cliente com base no nome e número.
    """
    last_sent_data = load_last_sent_dates()
    for entry in last_sent_data:
        if entry['name'] == name and entry['number'] == number:
            return datetime.strptime(entry['last_sent'], "%Y-%m-%d")
    return None

def update_last_sent_date(name, number):
    """
    Atualiza a última data de envio para um cliente.
    """
    last_sent_data = load_last_sent_dates()
    updated = False

    # Atualiza a data se o cliente já existe
    for entry in last_sent_data:
        if entry['name'] == name and entry['number'] == number:
            entry['last_sent'] = datetime.now().strftime("%Y-%m-%d")
            updated = True
            break

    # Adiciona um novo cliente se não existir
    if not updated:
        last_sent_data.append({
            'name': name,
            'number': number,
            'last_sent': datetime.now().strftime("%Y-%m-%d")
        })

    save_last_sent_dates(last_sent_data)