import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException, WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import urllib.parse
from datetime import datetime
import time
from rescheduling import check_reschedule  # Função que bloqueia o envio se o cliente estiver reagendado
from notifications import record_success, record_failure

load_dotenv()

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
EMAIL_LOGIN = os.getenv('EMAIL_LOGIN')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
FINANCIAL_EMAIL = os.getenv('FINANCIAL_EMAIL')

def critical_failure(error_message):
    non_critical_errors = [
        "no such window",
        "no such element",
        "element not interactable",
        "timed out after x seconds waiting for element to be clickable",
        "web view not found",
        "stale element reference",
        "unknown error",
        "element click intercepted",
        "is not clickable",
        "Connection refused",
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
    except smtplib.SMTPAuthenticationError:
        print(f"Erro de autenticação ao enviar email para {recipient_email}. Verifique suas credenciais.")
    except Exception as e:
        print(f"Falha ao enviar email para {recipient_email}: {str(e)}")

service = Service(ChromeDriverManager().install())

def send_messages(browser, customers):
    """
    Envia mensagens via WhatsApp para clientes com boletos vencidos.
    Se houver uma falha, envia uma notificação por email ao funcionário e ao cliente.
    """
    try:
        browser.get('https://web.whatsapp.com/')
    except (NoSuchWindowException, WebDriverException) as e:
        print(f"Erro ao abrir o WhatsApp Web: {e}")
        return

    for customer in customers:
        id = customer['id']
        name = customer['name']
        number = customer['number']
        days_late = customer['days_late']
        email = customer.get('email')

        # Verifica se o cliente está reagendado (NÃO enviar se a data reagendada ainda não passou)
        if check_reschedule(name=name, number=number):
            print(f'Cliente {name} reagendado, ignorando até nova data.')
            continue

        # Lógica de envio de mensagens para clientes com 3 dias ou mais de atraso
        if days_late >= 3:
            message = f'Olá {name}, \nO seu pagamento está em atraso há {days_late} dias. Por favor, regularize sua situação respondendo a esta mensagem. \nAtenciosamente, \nFinanceiro TS Distribuidora.'
            quote = urllib.parse.quote_plus(message)
            url = f'https://web.whatsapp.com/send?phone={number}&text={quote}'

            try:
                print(f'Enviando mensagem para {name} ({number})')
                browser.get(url)

                send_button = None
                for attempt in range(3):
                    try:
                        send_button = WebDriverWait(browser, 40).until(
                            EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                        )
                        browser.execute_script("arguments[0].scrollIntoView();", send_button)
                        send_button.click()
                        time.sleep(10)
                        break 
                    except StaleElementReferenceException:
                        print(f"O botão de envio expirou para {name}. Tentando novamente (tentativa {attempt + 1}/3)")

                if not send_button:
                    raise Exception("Número não é WhatsApp")

                # Se a mensagem foi enviada com sucesso
                record_success(id, name, number)

            except Exception as e:
                error_message = str(e)
                print(f"Erro ao enviar mensagem para {name} ({number}): {str(e)}")
                record_failure(id, name, number, str(e))

                if critical_failure(error_message):
                    email_subject = f"Notificação: WhatsApp não enviado - Falha ({name})"
                    email_body = f"O número {number} do cliente {name} apresentou um erro. Verifique se o número está correto, caso contrário, por favor entre em contato com o cliente e atualize o número no cadastro."
                    send_email(email_subject, email_body, FINANCIAL_EMAIL)

                    if email:
                        client_email_subject = "Notificação de atraso de pagamento"
                        client_email_body = f"""
                    Olá {name},

                    Verificamos que o seu pagamento está em atraso há {days_late} dias.

                    Por favor, regularize a sua situação. Caso tenha dúvidas, entre em contato conosco.

                    Atenciosamente, 

                    Financeiro TS Distribuidora.
                    """
                        send_email(client_email_subject, client_email_body, email)
                    else:
                        print(f"Email do cliente {name} está vazio, não será enviado.")
        else:
            print(f'Cliente {name} com {days_late} dias de atraso. Mensagens enviadas apenas depois de 6 dias de atraso.')
