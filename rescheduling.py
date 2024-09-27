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
    return False

def remove_reschedule_if_expired(name_customer=None, number_customer=None):
    """
    Remove um cliente do arquivo de reagendamentos se o reagendamento já tiver expirado.
    """
    rescheduling = load_rescheduling()
    rescheduling_updated = []

    for reschedule in rescheduling:
        new_date = datetime.strptime(reschedule['new_date_reschedule'], '%Y-%m-%d').date()

        # Verifica se o reagendamento expirou ou se corresponde ao cliente específico
        if new_date >= datetime.now().date() or \
           (reschedule['name'] == name_customer or reschedule['number'] == number_customer):
            rescheduling_updated.append(reschedule)

    save_rescheduling(rescheduling_updated)
