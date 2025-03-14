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
from datetime import datetime, timedelta
import time
from rescheduling import check_reschedule, get_last_sent_date, update_last_sent_date
from notifications import record_success, record_failure

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
        record_email_success(recipient_email)
        print(f"Email enviado com sucesso para {recipient_email}")
    except smtplib.SMTPAuthenticationError:
        print(f"Erro de autenticação ao enviar email para {recipient_email}. Verifique suas credenciais.")
    except Exception as e:
        print(f"Falha ao enviar email para {recipient_email}: {str(e)}")

service = Service(ChromeDriverManager().install())

def send_messages(browser, customers):
    try:
        browser.get('https://web.whatsapp.com/')
    except (NoSuchWindowException, WebDriverException) as e:
        print(f"Erro ao abrir o WhatsApp Web: {e}")
        return

    max_retries = 5
    for attempt in range(max_retries):
        try:
            WebDriverWait(browser, 50).until(EC.presence_of_element_located((By.ID, "side")))
            break
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(10)

    for customer in customers:
        name = customer['name']
        number = customer['number']
        boletos = customer['boletos']
        total_days_late = customer['total_days_late']
        value = customer['value']
        email = customer.get('email')

        if check_reschedule(name=name, number=number):
            print(f'Cliente {name} reagendado, ignorando até nova data.')
            continue

        if check_payment_status(name_customer=name, number_customer=number):
            print(f"Cliente {name} pagou o boleto. Removendo da lista ou ignorando.")
            remove_reschedule_if_expired(name_customer=name, number_customer=number)
            continue

        message = f"""Prezado(a) {name}, bom dia.

Estamos entrando em contato para informar que há {boletos} boleto(s) em aberto conosco com {total_days_late} dias de atraso.

O boleto com maior atraso é de R$ {value:.2f}.

Gostaríamos de solicitar a gentileza de regularizar esta pendência o mais breve possível.

Atenciosamente,

Financeiro TS Distribuidora.

***Caso já tenha realizado o pagamento, pedimos que ignore essa mensagem, pois o sistema leva até 2 dias úteis para confirmar a transação e atualizar o seu cadastro. """
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

            record_success(name, number)

        except Exception as e:
            error_message = str(e)
            print(f"Erro ao enviar mensagem para {name} ({number}): {str(e)}")
            record_failure(name, number, str(e))

            if critical_failure(error_message):
                email_subject = f"Notificação: WhatsApp não enviado - Falha ({name}, {number})"
                email_body = f"""Houve uma falha no envio da mensagem via WhatsApp para o cliente abaixo:

Nome: {name}
Número: {number}

Por favor, tome as medidas necessárias para garantir que o cliente seja informado por outros meios.

Atenciosamente,

Automation TS. """
                send_email(email_subject, email_body, FINANCIAL_EMAIL)

                if email:
                    client_email_subject = "Notificação de atraso de pagamento"
                    client_email_body = f"""Prezado(a) {name}, bom dia.

Estamos entrando em contato para informar que há {boletos} boleto(s) em aberto conosco com {total_days_late} dias de atraso.

O boleto com maior atraso é de R$ {value:.2f}.

Gostaríamos de solicitar a gentileza de regularizar esta pendência o mais breve possível.

Atenciosamente,

Financeiro TS Distribuidora.

***Caso já tenha realizado o pagamento, pedimos que ignore essa mensagem, pois o sistema leva até 2 dias úteis para confirmar a transação e atualizar o seu cadastro. """
                    try:
                        send_email(client_email_subject, client_email_body, email)
                    except Exception as e:
                        print(f"Falha ao enviar email para {email}: {str(e)}")
                        email_subject = f"Notificação: Falha no envio de email para o cliente ({name}, {email})"
                        email_body = f"""Houve uma falha no envio do email para o cliente abaixo:

Nome: {name}
Email: {email}

Erro: {str(e)}

Por favor, tome as medidas necessárias para garantir que o cliente seja informado por outros meios.

Atenciosamente,

Automation TS. """
                        send_email(email_subject, email_body, FINANCIAL_EMAIL)
                else:
                    print(f"Email do cliente {name} está vazio, não será enviado.")
                    email_subject = f"Notificação: Email do cliente vazio ({name}, {number})"
                    email_body = f"""O email do cliente abaixo está vazio:

Nome: {name}
Número: {number}

Por favor, tome as medidas necessárias para garantir que o cliente seja informado por outros meios.

Atenciosamente,

Automation TS. """
                    send_email(email_subject, email_body, FINANCIAL_EMAIL)

def send_due_date_alerts(browser):
    reminders = get_due_date_reminders()

    for reminder in reminders:
        name = reminder['name']
        number = reminder['number']
        boletos = reminder['boletos']
        #due_date = reminder['due_date'].strftime('%d/%m/%Y')  # Linha comentada mantida
        #value = reminder['value']  # Linha comentada mantida
        email = reminder.get('email')

        message = f"""Prezado(a) {name}, bom dia!

Nosso contato é de gratidão pela nossa parceria, aproveitamos para lembrá-lo que existe(m) {boletos} boletos a vencer em cinco dias.

Agradecemos a preferência e desejamos excelentes negócios.

Canal de Atendimento (85) 99842346.

Atenciosamente,

Financeiro TS Distribuidora. """
        quote = urllib.parse.quote_plus(message)
        url = f'https://web.whatsapp.com/send?phone={number}&text={quote}'

        try:
            print(f'Enviando alerta de vencimento para {name} ({number})')
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

            record_success(name, number)

        except Exception as e:
            error_message = str(e)
            print(f"Erro ao enviar alerta de vencimento para {name} ({number}): {str(e)}")
            record_failure(name, number, str(e))

            if critical_failure(error_message):
                email_subject = f"Notificação: WhatsApp não enviado - Falha ({name}, {number})"
                email_body = f"""Houve uma falha no envio da mensagem via WhatsApp para o cliente abaixo:

Nome: {name}
Número: {number}

Por favor, tome as medidas necessárias para garantir que o cliente seja informado por outros meios.

Atenciosamente,

Automation TS. """
                send_email(email_subject, email_body, FINANCIAL_EMAIL)

                if email:
                    client_email_subject = "Aviso de Vencimento de Boleto"
                    client_email_body = f"""Prezado(a) {name}, bom dia!

Nosso contato é de gratidão pela nossa parceria, aproveitamos para lembrá-lo que existe(m) {boletos} boletos a vencer em cinco dias.

Agradecemos a preferência e desejamos excelentes negócios.

Canal de Atendimento (85) 99842346.

Atenciosamente,

Financeiro TS Distribuidora. """
                    try:
                        send_email(client_email_subject, client_email_body, email)
                    except Exception as e:
                        send_email(email_subject, email_body, FINANCIAL_EMAIL)
                        print(f"Email do cliente {name} está vazio, não será enviado.")
                        email_subject = f"Notificação: Email do cliente vazio ({name}, {number})"
                        email_body = f"""O email do cliente abaixo está vazio:

Nome: {name}
Número: {number}

Por favor, tome as medidas necessárias para garantir que o cliente seja informado por outros meios.

Atenciosamente,

Automation TS. """
                        send_email(email_subject, email_body, FINANCIAL_EMAIL)
