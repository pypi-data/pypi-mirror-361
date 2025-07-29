import os
import urllib.request
import zipfile

def install_chromium():
    print("[*] Downloading Chromium and ChromeDriver...")

    base = os.path.dirname(os.path.abspath(__file__))
    chrome_url = "https://github.com/RobRich999/Chromium_Clang/releases/download/124.0.6367.118-r1230297/chrome-linux.zip"
    driver_url = "https://chromedriver.storage.googleapis.com/124.0.6367.118/chromedriver_linux64.zip"

    chrome_zip = os.path.join(base, "chrome.zip")
    driver_zip = os.path.join(base, "driver.zip")

    urllib.request.urlretrieve(chrome_url, chrome_zip)
    urllib.request.urlretrieve(driver_url, driver_zip)

    with zipfile.ZipFile(chrome_zip, 'r') as zip_ref:
        zip_ref.extractall(os.path.join(base, "chrome-linux"))

    with zipfile.ZipFile(driver_zip, 'r') as zip_ref:
        zip_ref.extractall(os.path.join(base, "chromedriver-linux"))

    os.remove(chrome_zip)
    os.remove(driver_zip)

    os.chmod(os.path.join(base, "chrome-linux", "chrome"), 0o755)
    os.chmod(os.path.join(base, "chromedriver-linux", "chromedriver"), 0o755)

    print("[✓] Chromium setup complete.")
