import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException, WebDriverException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import urllib.parse
from datetime import datetime
import time
from rescheduling import check_reschedule, remove_reschedule_if_expired
from notifications import record_success, record_failure
from database import check_payment_status

# Configuração do envio de email
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
EMAIL_LOGIN = os.getenv('EMAIL_LOGIN')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
FINANCIAL_EMAIL = os.getenv('FINANCIAL_EMAIL')

def critical_failure(error_message):
    non_critical_errors = [
        "no such window", "no such element", "element not interactable", 
        "timed out after x seconds waiting for element to be clickable", 
        "web view not found", "stale element reference", "unknown error", 
        "element click intercepted", "is not clickable", "Connection refused"
    ]
    
    for non_critical in non_critical_errors:
        if non_critical in error_message.lower():
            return False
    return True

def send_email(subject, body, recipient_email):
    if not recipient_email:
        print("Erro ao obter email do destinatário, campo vazio.")
        return

    msg = MIMEMultipart()
    msg['From'] = EMAIL_LOGIN
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_LOGIN, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email enviado com sucesso para {recipient_email}")
    except Exception as e:
        print(f"Falha ao enviar email para {recipient_email}: {str(e)}")

service = Service(ChromeDriverManager().install())

def send_messages(browser, customers):
    """
    Envia mensagens via WhatsApp para clientes com boletos vencidos.
    Mensagens são enviadas para clientes com mais de 3 dias e menos de 60 dias de atraso.
    """
    try:
        browser.get('https://web.whatsapp.com/')
        time.sleep(10)
    except (NoSuchWindowException, WebDriverException) as e:
        print(f"Erro ao abrir o WhatsApp Web: {e}")
        return

    for customer in customers:
        name = customer['name']
        number = customer['number']
        days_late = customer['days_late']
        email = customer.get('email')

        # Verifica se o cliente está reagendado
        if check_reschedule(name=name, number=number):
            print(f'Cliente {name} reagendado, ignorando até nova data.')
            continue

        # Verifica se o cliente pagou o boleto
        if check_payment_status(name_customer=name, number_customer=number):
            print(f"Cliente {name} pagou o boleto. Removendo da lista ou ignorando.")
            remove_reschedule_if_expired(name_customer=name, number_customer=number)
            continue

        # Preparando a mensagem
        message = f"""Prezado(a) {name}, bom dia.

Estamos entrando em contato para informar que há um valor em aberto conosco há {days_late} dias.

Gostaríamos de solicitar a gentileza de regularizar esta pendência o mais breve possível.

Atenciosamente, 

Financeiro TS Distribuidora.

***Caso já tenha realizado o pagamento, pedimos que ignore essa mensagem, pois o sistema leva até 2 dias úteis para confirmar a transação e atualizar o seu cadastro.
        """
        quote = urllib.parse.quote_plus(message)
        url = f'https://web.whatsapp.com/send?phone={number}&text={quote}'

        try:
            print(f'Enviando mensagem para {name} ({number})')
            browser.get(url)

            # Reduz o tempo de espera para melhorar a performance
            try:
                send_button = WebDriverWait(browser, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                )
                browser.execute_script("arguments[0].scrollIntoView();", send_button)
                send_button.click()
                time.sleep(10)
            except TimeoutException:
                print(f"Tempo excedido para encontrar o botão de envio para {name}. Tentando o próximo cliente.")
                continue  # Passa para o próximo cliente sem quebrar o loop
            
            record_success(name, number)

        except Exception as e:
            error_message = str(e)
            print(f"Erro ao enviar mensagem para {name} ({number}): {str(e)}")
            record_failure(name, number, str(e))

            # Envia email em caso de falha crítica
            if critical_failure(error_message):
                email_subject = f"Notificação: WhatsApp não enviado - Falha para {name}"
                email_body = f"O número {number} do cliente {name} apresentou um erro. Verifique se o número está correto, ou atualize-o."
                send_email(email_subject, email_body, FINANCIAL_EMAIL)

                if email:
                    client_email_subject = "Notificação de atraso de pagamento - TS Distribuidora"
                    client_email_body = f"""Prezado(a) {name}, bom dia.

Estamos entrando em contato para informar que há um valor em aberto conosco há {days_late} dias.

Gostaríamos de solicitar a gentileza de regularizar esta pendência o mais breve possível.

Atenciosamente, 

Financeiro TS Distribuidora.

***Caso já tenha realizado o pagamento, pedimos que ignore essa mensagem, pois o sistema leva até 2 dias úteis para confirmar a transação e atualizar o seu cadastro.
                    """
                    send_email(client_email_subject, client_email_body, email)
                else:
                    print(f"Email do cliente {name} está vazio, não será enviado.")
