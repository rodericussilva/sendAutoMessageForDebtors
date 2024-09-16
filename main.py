from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from whatsapp import send_messages
from database import search_debtors

def main():
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    customers = search_debtors()

    send_messages(browser, customers)
    browser.quit()

if __name__ == "__main__":
    main()