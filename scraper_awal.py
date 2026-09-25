import os
import json
import re
from datetime import datetime, timedelta
import requests

# Domain utama landing page
TARGET_URL = "https://warna.design/"
OUTPUT_FILE = "data/paito_master.json"
CUTOFF_DATE = datetime(2026, 9, 1)
START_DATE_ESTIMATE = datetime(2024, 1, 1)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://warna.design/"
}

def fetch_data():
    """
    Mengambil data dari landing page warna.design.
    Mencoba mengambil via endpoint API internal landing page terlebih dahulu.
    """
    print(f"[+] Membuka Landing Page: {TARGET_URL} ...")
    session = requests.Session()
    
    # List kemungkinan endpoint API data paito HK yang dipakai landing page
    api_endpoints = [
        "https://warna.design/api/paito/hk",
        "https://warna.design/api/hk",
        "https://warna.design/data/hk.json",
        TARGET_URL
    ]
    
    raw_draws = []
    
    for url in api_endpoints:
        try:
            res = session.get(url, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                # Jika response berupa JSON API
                try:
                    data = res.json()
                    text_data = json.dumps(data)
                    found = re.findall(r'\b\d{4}\b', text_data)
                    if len(found) > 50:
                        print(f"[+] Berhasil mengambil data via API/JSON endpoint: {url}")
                        return found
                except Exception:
                    # Jika response berupa HTML landing page biasa
                    found = re.findall(r'\b\d{4}\b', res.text)
                    if len(found) > len(raw_draws):
                        raw_draws = found
        except Exception as e:
            continue
            
    print(f"[+] Total raw result 4D terekstraksi dari landing page: {len(raw_draws)} angka.")
    return raw_draws

def process_and_assign_dates(raw_draws):
    paito_master = []
    current_date = START_DATE_ESTIMATE

    for idx, draw in enumerate(raw_draws):
        if current_date > CUTOFF_DATE:
            print(f"[!] Reached cutoff date: {CUTOFF_DATE.strftime('%Y-%m-%d')}. Stopping extraction.")
            break

        digits = [int(d) for d in draw]
        paito_master.append({
            "periode": idx + 1,
            "tanggal": current_date.strftime("%Y-%m-%d"),
            "result": draw,
            "as": digits[0],
            "kop": digits[1],
            "kepala": digits[2],
            "ekor": digits[3]
        })
        current_date += timedelta(days=1)

    return paito_master

def save_to_json(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[✔] Berhasil menyimpan {len(data)} baris data paito ke file: '{filepath}'")

def run_scraper():
    raw_draws = fetch_data()
    if not raw_draws:
        print("[-] Tidak ada data angka yang berhasil diekstraksi dari landing page.")
        return

    processed_data = process_and_assign_dates(raw_draws)
    save_to_json(processed_data, OUTPUT_FILE)

if __name__ == "__main__":
    run_scraper()
