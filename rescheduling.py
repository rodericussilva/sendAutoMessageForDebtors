import json
from datetime import datetime

RESCHEDULING_FILE = 'rescheduling.json'

def load_rescheduling():
    """
    Carrega os reagendamentos existentes de um arquivo JSON. 
    Se o arquivo estiver vazio ou corrompido, retorna uma lista vazia.
    """
    try:
        with open(RESCHEDULING_FILE, 'r') as file:
            content = file.read().strip()  # Remove espaços em branco e novas linhas
            if not content:  # Se o arquivo estiver vazio
                return []
            data = json.loads(content)
            return data.get('reagendamentos', []) if isinstance(data, dict) else []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        # Se houver erro na leitura do JSON, retornar uma lista vazia
        print(f"Erro ao carregar {RESCHEDULING_FILE}: Arquivo corrompido ou inválido.")
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

        if new_date >= datetime.now().date() or \
           (reschedule['name'] == name_customer or reschedule['number'] == number_customer):
            rescheduling_updated.append(reschedule)

    save_rescheduling(rescheduling_updated)
