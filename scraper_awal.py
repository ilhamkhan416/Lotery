import os
import json
import re
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

# URL diperbarui ke domain utama warna.design
TARGET_URL = "https://warna.design/"
OUTPUT_FILE = "data/paito_master.json"
CUTOFF_DATE = datetime(2026, 9, 1)
START_DATE_ESTIMATE = datetime(2024, 1, 1)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
}

def fetch_paito_html(url):
    print(f"[+] Membuka URL: {url} ...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"[-] Gagal mengambil halaman web: {e}")
        return None

def parse_and_clean_draws(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    if not table:
        print("[-] Tabel paito tidak ditemukan dalam struktur HTML.")
        return []

    raw_draws = []
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all(['td', 'th'])
        for col in cols:
            text = col.get_text(strip=True)
            digits = re.findall(r'\b\d{4}\b', text)
            if digits:
                raw_draws.append(digits[0])

    print(f"[+] Total raw result 4D terekstraksi: {len(raw_draws)} angka.")
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
    html = fetch_paito_html(TARGET_URL)
    if not html:
        return

    raw_draws = parse_and_clean_draws(html)
    if not raw_draws:
        print("[-] Tidak ada data angka yang berhasil diekstraksi.")
        return

    processed_data = process_and_assign_dates(raw_draws)
    save_to_json(processed_data, OUTPUT_FILE)

if __name__ == "__main__":
    run_scraper()
