import json
import os
import time
from google_play_scraper import search, app

# Kata kunci radar untuk menjaring aplikasi populer di tiap kategori
RADAR_KEYWORDS = [
    # Books & Education
    'e-book', 'novel indonesia', 'belajar bahasa', 'kursus online',
    # Productivity & Tools
    'catatan harian', 'pdf reader', 'scanner dokumen', 'pembersih hp', 'vpn gratis',
    # Business & Lifestyle
    'pencatat keuangan', 'kasir toko', 'jadwal sholat', 'kalkulator resep',
    # Entertainment & Trivia
    'kuis alkitab', 'tebak kata', 'streaming lokal'
]

discovered_packages = set()

print("🔍 Memulai Radar Market Analysis Google Play Store...")

# 1. Pindai Aplikasi berdasarkan Kata Kunci Radar (Ganti metode index() yang tidak stabil)
for kw in RADAR_KEYWORDS:
    try:
        print(f"📡 Memindai Kata Kunci: [{kw}]...")
        results = search(kw, lang='en', country='us', n_hits=20)
        
        for item in results:
            if isinstance(item, dict) and 'appId' in item:
                discovered_packages.add(item['appId'])
                
        time.sleep(1) # Delay aman agar tidak di-block Play Store
    except Exception as e:
        print(f"⚠️ Gagal memindai keyword '{kw}': {e}")
        continue

print(f"\n🎯 Berhasil menemukan {len(discovered_packages)} aplikasi unik dari radar!\n")

# 2. Baca Database Lama (jika ada) untuk Kalkulasi Delta Recent Downloads
old_data_map = {}
if os.path.exists("database.json"):
    try:
        with open("database.json", "r", encoding="utf-8") as f:
            old_list = json.load(f)
            if isinstance(old_list, list):
                for item in old_list:
                    if isinstance(item, dict) and "package" in item:
                        old_data_map[item["package"]] = item.get("rawInstalls", 0)
    except Exception as e:
        print(f"⚠️ Catatan pembacaan database lama: {e}")

new_database = []

# 3. Ambil Metadata Detail Aplikasi
target_packages = list(discovered_packages)

for pkg in target_packages:
    try:
        data = app(pkg, lang='en', country='us')
        
        current_installs = data.get('realInstalls', 0)
        previous_installs = old_data_map.get(pkg, current_installs)
        recent_downloads = current_installs - previous_installs if current_installs >= previous_installs else 0
        
        new_database.append({
            "title": data.get('title', 'N/A'),
            "package": pkg,
            "category": data.get('genreId', 'OTHER'),
            "installsText": data.get('installs', '0+'),
            "rawInstalls": current_installs,
            "recentDownloads": recent_downloads,
            "releaseDate": str(data.get('released', 'N/A')),
            "score": round(data.get('score', 0) or 0, 1),
            "reviews": f"{data.get('reviews', 0):,}",
            "asoScore": min(100, int((data.get('score', 0) or 0) * 20))
        })
        print(f"✅ Teranalisis: {data.get('title', '')[:30]}")
    except Exception as e:
        print(f"❌ Gagal mengambil detail {pkg}: {e}")
        continue

# 4. Simpan ke database.json
with open("database.json", "w", encoding="utf-8") as f:
    json.dump(new_database, f, ensure_ascii=False, indent=4)

print("\n🚀 Selesai! File database.json berhasil diperbarui.")
