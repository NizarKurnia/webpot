import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import datetime

TARGET_URL = "https://cbt37.sman37.sch.id/"
SAVE_DIR = "fake_web"
LOG_FILE = "logs/cloner.log"

os.makedirs("logs", exist_ok=True)

def log_clone_event(message):
    event = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "message": message
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

def safe_filename(path):
    """Buang query string, ambil nama file"""
    filename = os.path.basename(urlparse(path).path)
    return filename if filename else "index.html"

def clone_page(url, save_dir=SAVE_DIR):
    os.makedirs(save_dir, exist_ok=True)

    try:
        print(f"[+] Mulai clone {url}")
        log_clone_event(f"Mulai clone {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # akan raise error kalau status code bukan 200
    except requests.exceptions.RequestException as e:
        print(f"[!] Gagal akses {url}: {e}")
        log_clone_event(f"Gagal akses {url}: {e}")
        return

    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    tags = {"link": "href", "script": "src", "img": "src"}

    for tag, attr in tags.items():
        for resource in soup.find_all(tag):
            src = resource.get(attr)
            if not src:
                continue

            full_url = urljoin(url, src)
            parsed = urlparse(src)
            local_path = os.path.join(save_dir, parsed.path.lstrip("/"))

            if not os.path.basename(local_path):  
                continue

            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            try:
                r = requests.get(full_url, timeout=10)
                r.raise_for_status()
                with open(local_path, "wb") as f:
                    f.write(r.content)
                print(f"[+] Downloaded {full_url} -> {local_path}")
                log_clone_event(f"Downloaded {full_url} -> {local_path}")
            except requests.exceptions.RequestException as e:
                print(f"[!] Gagal download {full_url}: {e}")
                log_clone_event(f"Gagal download {full_url}: {e}")

    index_path = os.path.join(save_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
    log_clone_event(f"Clone selesai! Hasil ada di {index_path}")
    print("[+] Clone selesai! Hasil ada di", index_path)

# Tambahkan opsi multi-page cloning dan update otomatis
def clone_multiple(pages, base_url, save_dir=SAVE_DIR):
    for page in pages:
        clone_page(urljoin(base_url, page), save_dir)

def update_clone(url=TARGET_URL):
    print("[+] Memperbarui clone...")
    log_clone_event("Memperbarui clone...")
    clone_page(url)

if __name__ == "__main__":
    clone_page(TARGET_URL)

