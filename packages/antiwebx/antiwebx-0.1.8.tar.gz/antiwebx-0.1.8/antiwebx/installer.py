import os
import platform
import urllib.request
import zipfile
import shutil


def download_and_extract(url, extract_to, binary_name):
    try:
        zip_path = os.path.join(extract_to, "temp.zip")
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        os.remove(zip_path)

        if platform.system().lower() == "linux":
            for root, dirs, files in os.walk(extract_to):
                if binary_name in files:
                    os.chmod(os.path.join(root, binary_name), 0o755)
        return True
    except Exception as e:
        print(f"  ↳ Error downloading from: {url} → {e}\n    → failed, trying next...")
        return False


def detect_arch():
    system = platform.system().lower()
    machine = platform.machine().lower()

    if os.path.exists("/data/data/com.termux/files/usr"):
        return 'termux_arm64'

    if system == 'linux':
        if 'aarch64' in machine or 'arm64' in machine:
            return 'linux_arm64'
        return 'linux_x64'
    elif system == 'windows':
        return 'win_x64'
    elif system == 'darwin':
        if 'arm64' in machine:
            return 'mac_arm64'
        return 'mac_x64'
    else:
        raise RuntimeError("Unsupported OS/platform.")


def install_chromium():
    print("[*] Detecting platform and architecture...")
    arch_tag = detect_arch()
    print(f"[*] Detected platform → '{arch_tag}'")

    chrome_dir = os.path.join(os.getcwd(), "chrome")
    if os.path.exists(chrome_dir):
        shutil.rmtree(chrome_dir)
    os.makedirs(chrome_dir, exist_ok=True)

    chrome_links = {
        'termux_arm64': [
            # Custom Chromium builds that work on Termux
            "https://github.com/codes4education/termux-chromium-arm64/releases/download/v1.0/chrome-arm64.zip",
            "https://archive.org/download/chromium-arm64/chromium-arm64.zip"
        ],
        'linux_arm64': [
            "https://github.com/codes4education/termux-chromium-arm64/releases/download/v1.0/chrome-arm64.zip",
            "https://archive.org/download/chromium-arm64/chromium-arm64.zip"
        ],
        'linux_x64': [
            "https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/1245785/chrome-linux.zip",  # v138
            "https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/1238600/chrome-linux.zip",  # v134
            "https://github.com/RobRich999/Chromium_Clang/releases/download/124.0.6367.118-r1230297/chrome-linux.zip"
        ],
        'win_x64': [
            "https://github.com/macchrome/winchrome/releases/download/v138.0.6901.84-r1262078/Chrome-bin.zip",
            "https://github.com/macchrome/winchrome/releases/download/v134.0.6742.84-r1250166/Chrome-bin.zip",
            "https://github.com/macchrome/winchrome/releases/download/v124.0.6367.118-r1230297/Chrome-bin.zip"
        ],
        'mac_x64': [
            "https://github.com/ungoogled-software/ungoogled-chromium-macos/releases/download/124.0.6367.118-1/ungoogled-chromium_124.0.6367.118-1.mac_x64.zip"
        ],
        'mac_arm64': [
            "https://github.com/ungoogled-software/ungoogled-chromium-macos/releases/download/124.0.6367.118-1/ungoogled-chromium_124.0.6367.118-1.mac_arm64.zip"
        ]
    }

    print("[*] Downloading Chromium...")
    for url in chrome_links.get(arch_tag, []):
        print(f"  ↳ Trying: {url}")
        if download_and_extract(url, chrome_dir, "chrome" if 'linux' in arch_tag or 'termux' in arch_tag else "chrome.exe"):
            print("[✓] Chromium setup complete.")
            return

    raise RuntimeError("❌ All Chromium mirrors failed.")
