import json
from datetime import datetime

RESCHEDULING_FILE = 'rescheduling.json'
LAST_SENT_FILE = 'last_sent_dates.json'

def load_rescheduling():
    try:
        with open(RESCHEDULING_FILE, 'r') as file:
            data = json.load(file)
            return data.get('reagendamentos', []) if isinstance(data, dict) else []
    except FileNotFoundError:
        return []

def save_rescheduling(rescheduling):
    with open(RESCHEDULING_FILE, 'w') as file:
        json.dump({"reagendamentos": rescheduling}, file, indent=4)

def check_reschedule(name=None, number=None):
    rescheduling = load_rescheduling()
    for reagendamento in rescheduling:
        if (name and reagendamento.get('name') == name) or (number and reagendamento.get('number') == number):
            new_date = datetime.strptime(reagendamento['new_date_reschedule'], '%Y-%m-%d').date()
            if new_date > datetime.now().date():
                return True
    return False

def load_last_sent_dates():
    try:
        with open(LAST_SENT_FILE, 'r') as file:
            data = json.load(file)
            return data.get('clientes', [])
    except FileNotFoundError:
        return []

def save_last_sent_dates(last_sent_data):
    with open(LAST_SENT_FILE, 'w') as file:
        json.dump({"clientes": last_sent_data}, file, indent=4)

def get_last_sent_date(name, number):
    last_sent_data = load_last_sent_dates()
    for entry in last_sent_data:
        if entry['name'] == name and entry['number'] == number:
            return datetime.strptime(entry['last_sent'], "%Y-%m-%d")
    return None

def update_last_sent_date(name, number):
    last_sent_data = load_last_sent_dates()
    updated = False

    for entry in last_sent_data:
        if entry['name'] == name and entry['number'] == number:
            entry['last_sent'] = datetime.now().strftime("%Y-%m-%d")
            updated = True
            break

    if not updated:
        last_sent_data.append({
            'name': name,
            'number': number,
            'last_sent': datetime.now().strftime("%Y-%m-%d")
        })

    save_last_sent_dates(last_sent_data)
