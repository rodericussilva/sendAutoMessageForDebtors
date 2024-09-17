import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import urllib.parse
from datetime import datetime
import time
from rescheduling import check_reschedule
from notifications import record_success, record_failure

service = Service(ChromeDriverManager().install())

def send_messages(browser, customers):
    """
    :param browser: Instância do Selenium WebDriver
    :param clientes: Lista de dicionários contendo dados dos clientes
    """

    browser.get('https://web.whatsapp.com/')

    max_retries = 5

    for attempt in range(max_retries):
        try:

            WebDriverWait(browser, 50).until(EC.presence_of_element_located((By.ID, "side")))
            break
        except:
            if attempt == max_retries - 1:
                raise
            time.sleep(10)

    for curstomer in customers:
        id = curstomer['id']
        name = curstomer['name']
        number = curstomer['number']
        days_late = curstomer['days_late']

        if check_reschedule(name=name, number=number):
            print(f'Cliente {name} reagendado, ignorando até nova data')
            continue

        # Mensagem de cobrança - ver como ficará
        message = f'Olá {name}, \nO seu pagamento está em atraso há {days_late} dias. Por favor, regularize sua situação respondendo a esta mensagem. \nAtenciosamente, \nFinanceiro TS Distribuidora.'
        quote = urllib.parse.quote_plus(message)
        url = f'https://web.whatsapp.com/send?phone={number}&text={quote}'

        try:
            print(f'Enviando mensagem para {name} ({number})')
            browser.get(url)
            send_button = WebDriverWait(browser, 40).until(EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]')))
            time.sleep(10)
            browser.execute_script("arguments[0].scrollIntoView();", send_button)
            send_button.click()
            time.sleep(10)

            record_success(id, name, number)

        except Exception as e:
            record_failure(id, name, number, str(e))