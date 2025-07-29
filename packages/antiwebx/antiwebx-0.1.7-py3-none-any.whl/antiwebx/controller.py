import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import platform

def get_chrome_path():
    base = os.path.dirname(os.path.abspath(__file__))
    system = platform.system().lower()
    chrome_name = "chrome.exe" if system == "windows" else "chrome"
    for root, dirs, files in os.walk(os.path.join(base, "chrome")):
        if chrome_name in files:
            return os.path.join(root, chrome_name)
    return None

def get_driver_path():
    base = os.path.dirname(os.path.abspath(__file__))
    system = platform.system().lower()
    driver_name = "chromedriver.exe" if system == "windows" else "chromedriver"
    for root, dirs, files in os.walk(os.path.join(base, "chromedriver")):
        if driver_name in files:
            return os.path.join(root, driver_name)
    return None

def launch_browser(headless=True):
    chrome_path = get_chrome_path()
    driver_path = get_driver_path()

    if not chrome_path or not driver_path:
        raise RuntimeError("❌ Chrome or Chromedriver not found")

    options = Options()
    options.binary_location = chrome_path
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver
