import time
import json
import requests
from datetime import datetime

# Kaydedilecek JSON dosyalarının isimleri
FULL_LOG_FILE = "./InternetStatusRecord/full_log.json"
INTERVALS_FILE = "./InternetStatusRecord/intervals.json"

# Bellekte tutulacak kayıt listeleri
full_log = []
intervals = []
current_down_start = None

def check_internet():
    """
    Google’a HTTPS isteği atarak internet bağlantısını kontrol eder.
    5 saniye içerisinde yanıt alınamazsa bağlantı kesik sayılır.
    """
    try:
        response = requests.get("https://www.google.com", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def save_full_log():
    """full_log listesini FULL_LOG_FILE dosyasına yazar."""
    with open(FULL_LOG_FILE, "w+", encoding="utf-8") as f:
        json.dump(full_log, f, indent=2, ensure_ascii=False)

def save_intervals():
    """intervals listesini INTERVALS_FILE dosyasına yazar."""
    with open(INTERVALS_FILE, "w+", encoding="utf-8") as f:
        json.dump(intervals, f, indent=2, ensure_ascii=False)

print("Başlatılıyor: İnternet bağlantısı izleniyor. Çıkmak için Ctrl+C tuşuna basınız.")

try:
    while True:
        # Zamanı “YYYY-MM-DD HH:MM:SS” formatında alıyoruz
        now = datetime.now().isoformat(sep=' ', timespec='seconds')
        is_up = check_internet()
        status = "up" if is_up else "down"

        # 1) Tam kayıt: Zaman + durum
        full_log.append({
            "timestamp": now,
            "status": status
        })
        save_full_log()

        # 2) Aralık kaydı: Bağlantı kopuşu başladığında current_down_start atıyoruz,
        #    tekrar “up” olduğunda bu aralığı kaydedip current_down_start’ı temizliyoruz.
        if not is_up:
            if current_down_start is None:
                current_down_start = now
        else:
            if current_down_start is not None:
                intervals.append({
                    "start": current_down_start,
                    "end": now
                })
                current_down_start = None
                save_intervals()

        # 1 saniye bekle ve tekrar dene
        time.sleep(5)

except KeyboardInterrupt:
    print("\nİzleme durduruldu.")

    # Eğer script kapanırken hâlâ kesinti içindeysek, o anı bitiş zamanı olarak kaydedelim
    if current_down_start is not None:
        intervals.append({
            "start": current_down_start,
            "end": datetime.now().isoformat(sep=' ', timespec='seconds')
        })
        save_intervals()

    print("JSON dosyaları kaydedildi:")
    print(f"- Tam kayıt: {FULL_LOG_FILE}")
    print(f"- Kesinti aralıkları: {INTERVALS_FILE}")
