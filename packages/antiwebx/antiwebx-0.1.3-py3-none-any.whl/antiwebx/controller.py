import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from .installer import install_chromium

def setup_driver():
    base = os.path.dirname(os.path.abspath(__file__))
    chrome_path = os.path.join(base, "chrome-linux", "chrome")
    driver_path = os.path.join(base, "chromedriver-linux", "chromedriver")

    if not os.path.exists(chrome_path) or not os.path.exists(driver_path):
        install_chromium()

    options = Options()
    options.binary_location = chrome_path
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver
