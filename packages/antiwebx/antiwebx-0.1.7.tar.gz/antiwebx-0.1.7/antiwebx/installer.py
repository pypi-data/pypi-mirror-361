import os
import urllib.request
import zipfile
import platform
import shutil

def download_and_extract(url, extract_to, binary_name):
    try:
        file_zip = os.path.join(extract_to, "temp.zip")
        urllib.request.urlretrieve(url, file_zip)
        with zipfile.ZipFile(file_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        os.remove(file_zip)
        bin_path = find_binary(extract_to, binary_name)
        if bin_path:
            os.chmod(bin_path, 0o755)
        return True
    except Exception as e:
        print(f"  ↳ Error downloading from: {url} → {e}")
        return False

def find_binary(folder, binary_name):
    for root, dirs, files in os.walk(folder):
        if binary_name in files:
            return os.path.join(root, binary_name)
    return None

def install_chromium():
    print("[*] Detecting platform and architecture...")
    system = platform.system().lower()
    arch = platform.machine().lower()

    if 'aarch64' in arch or 'arm64' in arch:
        arch_tag = 'linux_arm64'
    elif 'arm' in arch:
        arch_tag = 'linux_arm'
    elif 'x86_64' in arch or 'amd64' in arch:
        arch_tag = 'linux_x64'
    elif 'win' in system:
        arch_tag = 'win_x64'
    elif 'darwin' in system and 'arm' in arch:
        arch_tag = 'mac_arm64'
    elif 'darwin' in system:
        arch_tag = 'mac_x64'
    else:
        raise RuntimeError(f"❌ Unsupported platform: {system}/{arch}")

    print(f"[*] Detected platform {system}/{arch} → using '{arch_tag}' build list")

    chrome_links = {
        'linux_x64': [
            "https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/1132442/chrome-linux.zip",
            "https://github.com/RobRich999/Chromium_Clang/releases/download/124.0.6367.118-r1230297/chrome-linux.zip"
        ],
        'linux_arm64': [
            "https://github.com/ekg/arm-chromium-build/releases/download/v124/chromium-browser-124.0.6367.207-1-aarch64.zip"
        ],
        'win_x64': [
            "https://github.com/macchrome/winchrome/releases/download/v124.0.6367.118-r1230297/Chrome-bin.zip"
        ],
        'mac_x64': [
            "https://github.com/ungoogled-software/ungoogled-chromium-macos/releases/download/124.0.6367.118-1/ungoogled-chromium_124.0.6367.118-1.mac_x64.zip"
        ],
        'mac_arm64': [
            "https://github.com/ungoogled-software/ungoogled-chromium-macos/releases/download/124.0.6367.118-1/ungoogled-chromium_124.0.6367.118-1.mac_arm64.zip"
        ]
    }

    driver_links = {
        'linux_x64': "https://chromedriver.storage.googleapis.com/124.0.6367.118/chromedriver_linux64.zip",
        'linux_arm64': "https://chromedriver.storage.googleapis.com/124.0.6367.118/chromedriver_linux64.zip",
        'win_x64': "https://chromedriver.storage.googleapis.com/124.0.6367.118/chromedriver_win32.zip",
        'mac_x64': "https://chromedriver.storage.googleapis.com/124.0.6367.118/chromedriver_mac64.zip",
        'mac_arm64': "https://chromedriver.storage.googleapis.com/124.0.6367.118/chromedriver_mac64_m1.zip"
    }

    base = os.path.dirname(os.path.abspath(__file__))
    chrome_dir = os.path.join(base, "chrome")
    driver_dir = os.path.join(base, "chromedriver")

    os.makedirs(chrome_dir, exist_ok=True)
    os.makedirs(driver_dir, exist_ok=True)

    chrome_success = False
    print("[*] Downloading Chromium...")
    for url in chrome_links.get(arch_tag, []):
        print(f"  ↳ Trying: {url}")
        if download_and_extract(url, chrome_dir, "chrome" if 'linux' in arch_tag else "chrome.exe"):
            chrome_success = True
            break
        else:
            print("    → failed, trying next...")
    if not chrome_success:
        raise RuntimeError("❌ All Chromium mirrors failed.")

    print("[*] Downloading ChromeDriver...")
    driver_url = driver_links.get(arch_tag)
    if not driver_url or not download_and_extract(driver_url, driver_dir, "chromedriver" if 'linux' in arch_tag else "chromedriver.exe"):
        raise RuntimeError("❌ ChromeDriver download failed.")

    print("[✓] Chromium setup complete.")
