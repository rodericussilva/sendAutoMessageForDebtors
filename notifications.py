from datetime import datetime

def record_success(id, name, number):

    with open('log_success.txt', 'a') as file:
        file.write(f"{datetime.now()} - Mensagem enviada com sucesso para {name} ({number}).\n")
    #print(f"Mensagem enviada com sucesso para {name} ({number}).")

def record_failure(id, name, number, error):

    with open('log_failure.txt', 'a') as file:
        file.write(f"{datetime.now()} - Falha ao enviar mensagem para {name} ({number}): {error}\n")
    #print(f"Falha ao enviar mensagem para {name} ({number}): {error}")
