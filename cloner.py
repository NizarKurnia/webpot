import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import datetime
import argparse
import logging
from logging.handlers import RotatingFileHandler
import pathlib
from pythonjsonlogger import jsonlogger

# defaults
TARGET_URL = "https://cbt37.sman37.sch.id/"
SAVE_DIR = "fake_web"
LOG_FILE = "logs/cloner.log"

# load optional config.json
try:
    cfg_path = pathlib.Path(__file__).parent / "config.json"
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as _f:
            _cfg = json.load(_f)
        TARGET_URL = _cfg.get("target_url", TARGET_URL)
        SAVE_DIR = _cfg.get("webroot", SAVE_DIR)
        LOG_FILE = _cfg.get("cloner_log", LOG_FILE)
except Exception:
    pass

os.makedirs("logs", exist_ok=True)

# setup logger
logger = logging.getLogger("webpot.cloner")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    handler.setFormatter(jsonlogger.JsonFormatter())
    logger.addHandler(handler)

def log_clone_event(message):
    event = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "msg": message
    }
    try:
        logger.info("", extra=event)
    except Exception:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

def safe_filename(path):
    """Return safe filename; default to index.html when path is folder"""
    parsed = urlparse(path)
    filename = os.path.basename(parsed.path)
    if not filename:
        return "index.html"
    return filename

def is_valid_url(url: str) -> bool:
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False

def clone_page(url, save_dir=SAVE_DIR):
    os.makedirs(save_dir, exist_ok=True)

    session = requests.Session()
    try:
        print(f"[+] Mulai clone {url}")
        log_clone_event(f"Mulai clone {url}")
        response = session.get(url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[!] Gagal akses {url}: {e}")
        log_clone_event(f"Gagal akses {url}: {e}")
        return

    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    # modify form actions to point to our local endpoint
    for form in soup.find_all("form"):
        try:
            form["action"] = "/"
        except Exception:
            pass

    tags = {"link": "href", "script": "src", "img": "src"}

    for tag, attr in tags.items():
        for resource in soup.find_all(tag):
            src = resource.get(attr)
            if not src:
                continue

            full_url = urljoin(url, src)
            parsed = urlparse(full_url)
            local_path = os.path.join(save_dir, parsed.path.lstrip("/"))

            # skip directories
            if not os.path.basename(local_path):
                continue

            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            try:
                r = session.get(full_url, timeout=15)
                r.raise_for_status()
                with open(local_path, "wb") as f:
                    f.write(r.content)
                print(f"[+] Downloaded {full_url} -> {local_path}")
                log_clone_event(f"Downloaded {full_url} -> {local_path}")
            except requests.exceptions.RequestException as e:
                print(f"[!] Gagal download {full_url}: {e}")
                log_clone_event(f"Gagal download {full_url}: {e}")
            except OSError as e:
                print(f"[!] File write error {local_path}: {e}")
                log_clone_event(f"File write error {local_path}: {e}")

    index_path = os.path.join(save_dir, "index.html")
    try:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        log_clone_event(f"Clone selesai! Hasil ada di {index_path}")
        print("[+] Clone selesai! Hasil ada di", index_path)
    except OSError as e:
        print(f"[!] Gagal tulis index.html: {e}")
        log_clone_event(f"Gagal tulis index.html: {e}")

# Tambahkan opsi multi-page cloning dan update otomatis
def clone_multiple(pages, base_url, save_dir=SAVE_DIR):
    for page in pages:
        clone_page(urljoin(base_url, page), save_dir)

def update_clone(url=TARGET_URL):
    print("[+] Memperbarui clone...")
    log_clone_event("Memperbarui clone...")
    clone_page(url)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple website cloner for WebPot")
    parser.add_argument("--url", help="Target URL to clone", default=TARGET_URL)
    parser.add_argument("--out", help="Output directory", default=SAVE_DIR)
    args = parser.parse_args()
    if not is_valid_url(args.url):
        print(f"[!] Invalid URL provided: {args.url}")
        log_clone_event(f"Invalid URL provided: {args.url}")
        raise SystemExit(1)
    clone_page(args.url, save_dir=args.out)

