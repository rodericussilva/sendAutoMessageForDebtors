import json
from datetime import datetime

RESCHEDULING_FILE = 'rescheduling.json'

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