import os
import json
import re
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

TARGET_URL = "https://warna.design/"
OUTPUT_FILE = "data/paito_master.json"
CUTOFF_DATE = datetime(2026, 9, 1)
START_DATE_ESTIMATE = datetime(2024, 1, 1)

def scrape_with_playwright():
    print(f"[+] Membuka browser Playwright untuk target: {TARGET_URL} ...")
    raw_draws = []
    
    with sync_playwright() as p:
        # Jalankan browser Chromium secara headless
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            # Beri jeda 5 detik agar seluruh script render tabel selesai
            page.wait_for_timeout(5000)
            
            # Ambil seluruh teks dari halaman yang sudah di-render JavaScript
            content_text = page.inner_text("body")
            
            # Ekstraksi seluruh pola 4 digit angka
            raw_draws = re.findall(r'\b\d{4}\b', content_text)
            print(f"[+] Total raw result 4D berhasil ditarik: {len(raw_draws)} angka.")
            
        except Exception as e:
            print(f"[-] Terjadi kesalahan saat render Playwright: {e}")
        finally:
            browser.close()
            
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
    raw_draws = scrape_with_playwright()
    if not raw_draws:
        print("[-] Tidak ada data yang berhasil diekstraksi.")
        return

    processed_data = process_and_assign_dates(raw_draws)
    save_to_json(processed_data, OUTPUT_FILE)

if __name__ == "__main__":
    run_scraper()
