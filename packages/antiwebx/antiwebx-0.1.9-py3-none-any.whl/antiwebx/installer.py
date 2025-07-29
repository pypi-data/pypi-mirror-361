import os
import platform
import urllib.request
import zipfile
import shutil

def install_chromium():
    print("[*] Detecting platform and architecture...")
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Determine platform key
    if 'aarch64' in machine or 'arm64' in machine:
        plat = "linux_arm64"
    elif 'x86_64' in machine or 'amd64' in machine:
        plat = "linux_x64"
    elif 'win' in system:
        plat = "win"
    else:
        raise RuntimeError("❌ Unsupported platform")

    print(f"[*] Detected platform → '{plat}'")

    # Setup paths
    base = os.getcwd()
    chrome_dir = os.path.join(base, "chrome")
    chrome_zip = os.path.join(base, "chrome.zip")

    if os.path.exists(chrome_dir):
        shutil.rmtree(chrome_dir)
    os.makedirs(chrome_dir, exist_ok=True)

    # Chromium ZIP Mirrors
    urls = []

    if plat == "linux_x64":
        urls = [
            # Latest working Chromium builds
            "https://github.com/macchrome/winchrome/releases/download/v138.0.0.0-r1400000/Linux_x64_1380000_chrome.zip",
            "https://github.com/macchrome/winchrome/releases/download/v137.0.0.0-r1390000/Linux_x64_1370000_chrome.zip",
            "https://github.com/macchrome/winchrome/releases/download/v136.0.0.0-r1380000/Linux_x64_1360000_chrome.zip",
            "https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/1175695/chrome-linux.zip",
        ]
    elif plat == "linux_arm64":
        urls = [
            # Termux compatible
            "https://archive.org/download/chromium-arm64/chromium-browser-124.0.6367.207-1-aarch64.zip"
        ]
    elif plat == "win":
        urls = [
            # Windows builds
            "https://github.com/macchrome/winchrome/releases/download/v138.0.0.0-r1400000/Win_x64_1380000_chrome.zip",
            "https://github.com/macchrome/winchrome/releases/download/v137.0.0.0-r1390000/Win_x64_1370000_chrome.zip",
        ]

    # Try each link
    print("[*] Downloading Chromium...")
    for url in urls:
        try:
            print(f"  ↳ Trying: {url}")
            urllib.request.urlretrieve(url, chrome_zip)
            print("  ✅ Download successful!")
            break
        except Exception as e:
            print(f"  ↳ Error downloading from: {url} → {e}\n    → failed, trying next...")
    else:
        raise RuntimeError("❌ All Chromium mirrors failed.")

    print("[*] Extracting Chromium...")
    try:
        with zipfile.ZipFile(chrome_zip, 'r') as zip_ref:
            zip_ref.extractall(chrome_dir)
    except zipfile.BadZipFile:
        raise RuntimeError("❌ Downloaded file was not a valid ZIP archive.")
    finally:
        os.remove(chrome_zip)

    # Make binaries executable
    for root, _, files in os.walk(chrome_dir):
        for file in files:
            if "chrome" in file.lower() or "chromium" in file.lower():
                try:
                    os.chmod(os.path.join(root, file), 0o755)
                except:
                    pass

    print("[✓] Chromium setup complete.")
