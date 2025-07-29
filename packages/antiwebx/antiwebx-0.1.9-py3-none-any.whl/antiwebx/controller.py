import os
import platform
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def launch_browser(headless=True):
    base_dir = os.path.join(os.getcwd(), "chrome")
    driver_dir = os.path.join(os.getcwd(), "chromedriver")

    chrome_bin = None
    driver_bin = None

    # Find Chromium binary
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.lower().startswith("chrome") and os.access(os.path.join(root, f), os.X_OK):
                chrome_bin = os.path.join(root, f)
                break

    # Find ChromeDriver binary
    for root, _, files in os.walk(driver_dir):
        for f in files:
            if "chromedriver" in f.lower() and os.access(os.path.join(root, f), os.X_OK):
                driver_bin = os.path.join(root, f)
                break

    # If chromedriver not found in folder, try system PATH
    if not driver_bin:
        driver_bin = shutil.which("chromedriver")

    if not chrome_bin:
        raise FileNotFoundError("❌ Chromium binary not found in ./chrome")
    if not driver_bin:
        raise FileNotFoundError("❌ ChromeDriver not found in ./chromedriver or system PATH")

    # Chrome Options
    options = Options()
    options.binary_location = chrome_bin

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

    # Stability flags
    flags = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-extensions",
        "--disable-infobars",
        "--disable-blink-features=AutomationControlled",
        "--remote-debugging-port=9222"
    ]
    for flag in flags:
        options.add_argument(flag)

    service = Service(executable_path=driver_bin)
    return webdriver.Chrome(service=service, options=options)
