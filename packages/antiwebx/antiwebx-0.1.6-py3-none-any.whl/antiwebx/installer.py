"""
antiwebx.installer
------------------
Download & unpack Chromium + ChromeDriver with
platform-aware fallback URLs and automatic retries.
"""

from __future__ import annotations
import os, platform, zipfile, urllib.request, urllib.error, shutil, sys, time

# ────────────────────────────────────────────────────────────────────────────
# CONFIG – add or change links here ↓↓↓
# ────────────────────────────────────────────────────────────────────────────

DOWNLOAD_MATRIX = {
    # Linux x86-64 (typical VPS / desktop)
    "linux_x64": {
        "chromium": [
            # Official Chrome for-testing
            "https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.57/linux64/chrome-linux64.zip",
            # RobRich nightly builds
            "https://github.com/RobRich999/Chromium_Clang/releases/download/124.0.6367.118-r1230297/chrome-linux.zip",
        ],
        "driver": [
            "https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.57/linux64/chromedriver-linux64.zip",
            "https://chromedriver.storage.googleapis.com/124.0.6367.118/chromedriver_linux64.zip",
        ],
    },

    # Termux / Android ARM64
    "linux_arm64": {
        "chromium": [
            # Chromium build maintained for aarch64
            "https://github.com/ekles/ungoogled-chromium-arm64/releases/download/124.0.6367.207-1/chromium-browser-124.0.6367.207-1-aarch64.zip",
        ],
        "driver": [
            # The driver is still x86-64; Selenium can run remote-debugging without driver,
            # but we provide one so scripts that require it don't break.
            "https://chromedriver.storage.googleapis.com/124.0.6367.118/chromedriver_linux64.zip",
        ],
    },

    # Windows x86-64
    "windows_x64": {
        "chromium": [
            "https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.57/win64/chrome-win64.zip",
        ],
        "driver": [
            "https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.57/win64/chromedriver-win64.zip",
        ],
    },
}

# Where to unpack relative to this file
CHROME_DIR   = "chrome"
DRIVER_DIR   = "chromedriver"

# ────────────────────────────────────────────────────────────────────────────
# Helper functions
# ────────────────────────────────────────────────────────────────────────────

def _download(url: str, dest: str) -> bool:
    """Try to download *url* to *dest*. Return True on success, False on 404/403."""
    try:
        with urllib.request.urlopen(url, timeout=60) as r, open(dest, "wb") as f:
            shutil.copyfileobj(r, f)
        return True
    except urllib.error.HTTPError as e:
        if e.code in (403, 404):
            print(f"  ↳ {e.code} on {url.split('/')[-1]} – trying next mirror…")
            return False
        raise  # network error, let it propagate
    except Exception as e:
        print(f"  ↳ error: {e}")
        return False


def _unzip(zip_path: str, out_dir: str) -> None:
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(out_dir)
    os.remove(zip_path)


def _ensure_exec(bin_path: str) -> None:
    if os.path.exists(bin_path):
        os.chmod(bin_path, os.stat(bin_path).st_mode | 0o755)

# ────────────────────────────────────────────────────────────────────────────
# Public API
# ────────────────────────────────────────────────────────────────────────────

def install_chromium(force: bool = False) -> None:
    """
    Download + extract Chromium & ChromeDriver if not already present.
    • *force*=True will re-download even if folders exist.
    """

    base = os.path.dirname(os.path.abspath(__file__))
    chrome_home  = os.path.join(base, CHROME_DIR)
    driver_home  = os.path.join(base, DRIVER_DIR)

    if not force and os.path.isdir(chrome_home) and os.path.isdir(driver_home):
        print("[✓] Chromium already installed.")
        return

    # Clean old dirs if forcing
    if force and os.path.isdir(chrome_home):
        shutil.rmtree(chrome_home, ignore_errors=True)
    if force and os.path.isdir(driver_home):
        shutil.rmtree(driver_home, ignore_errors=True)

    # Detect platform key
    plat = platform.system().lower()
    arch = platform.machine().lower()
    key  = {
        ("linux", "x86_64"): "linux_x64",
        ("linux", "aarch64"): "linux_arm64",
        ("linux", "arm64"):   "linux_arm64",
        ("windows", "amd64"): "windows_x64",
    }.get((plat, arch))

    if not key or key not in DOWNLOAD_MATRIX:
        raise RuntimeError(f"Unsupported platform: {plat}/{arch}")

    print(f"[*] Detected platform {plat}/{arch} → using '{key}' build list")
    urls = DOWNLOAD_MATRIX[key]

    # Download loop with fallbacks
    chrome_zip = os.path.join(base, "chrome.zip")
    driver_zip = os.path.join(base, "driver.zip")

    for link in urls["chromium"]:
        if _download(link, chrome_zip):
            break
    else:
        raise RuntimeError("❌ All Chromium mirrors failed.")

    for link in urls["driver"]:
        if _download(link, driver_zip):
            break
    else:
        print("⚠️  All ChromeDriver mirrors failed. Proceeding without driver.")

    # Unpack
    _unzip(chrome_zip, chrome_home)
    if os.path.exists(driver_zip):
        _unzip(driver_zip, driver_home)

    # make executable
    _ensure_exec(os.path.join(chrome_home, "chrome"))
    _ensure_exec(os.path.join(driver_home, "chromedriver"))

    print("[✓] Chromium setup complete.")

# Quick CLI entry-point
if __name__ == "__main__":
    start = time.time()
    install_chromium(force=False)
    print(f"Done in {time.time()-start:.1f}s")
