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
    Verifica se o cliente está reagendado e se a data reagendada já passou.
    
    :return: True se o cliente ainda estiver reagendado e a data não passou, False caso contrário.
    """
    rescheduling = load_rescheduling()
    for reagendamento in rescheduling:
        if (name and reagendamento.get('name') == name) or (number and reagendamento.get('number') == number):
            new_date = datetime.strptime(reagendamento['new_date_reschedule'], '%Y-%m-%d').date()
            if new_date > datetime.now().date():
                # Se a data reagendada ainda não passou, retornar True para impedir o envio
                return True
    # Se a data já passou ou não está reagendado, retornar False para permitir o envio
    return False
