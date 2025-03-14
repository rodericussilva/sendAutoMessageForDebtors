from datetime import datetime

def record_success(id, name, number):

    with open('log_success.txt', 'a') as file:
        file.write(f"{datetime.now()} - Mensagem enviada com sucesso para {name} ({number}).\n")

def record_failure(id, name, number, error):

    with open('log_failure.txt', 'a') as file:
        file.write(f"{datetime.now()} - Falha ao enviar mensagem para {name} ({number}): {error}\n")

def record_email_success(recipient_email):
    
    with open('log_email_success.txt', 'a') as file:
        file.write(f"{datetime.now()} - Email enviado com sucesso para {recipient_email}\n")
        
def record_email_failure(email, error_message):
    
    with open('log_email_failure.txt', 'a') as file:
        file.write(f"Falha ao enviar email para {email}: {error_message}\n")
