import json
import os
import time
from google_play_scraper import index, app

# Kategori Google Play Store yang dipindai secara otomatis
CATEGORIES = [
    'BOOKS_AND_REFERENCE',
    'EDUCATION',
    'LIFESTYLE',
    'TOOLS',
    'PRODUCTIVITY',
    'GAME_TRIVIA',
    'BUSINESS',
    'ENTERTAINMENT'
]

COLLECTIONS = [
    'topselling_free',
    'topgrossing'
]

discovered_packages = set()

print("🔍 Memulai Radar Market Analysis Google Play Store...")

# 1. Sapu Chart & Kategori Otomatis (Zero Input)
for cat in CATEGORIES:
    for col in COLLECTIONS:
        try:
            print(f"📡 Memindai Kategori: [{cat}] -> {col}...")
            results = index(
                category=cat,
                collection=col,
                lang='en',
                country='us'
            )
            for item in results:
                discovered_packages.add(item['appId'])
            time.sleep(0.5)  # Delay aman agar tidak memicu rate-limit
        except Exception:
            continue

print(f"\n🎯 Berhasil menemukan {len(discovered_packages)} aplikasi unik dari radar pasar!\n")

# 2. Muat Data Lama untuk Menghitung Delta Recent Downloads (30 Hari)
old_data_map = {}
if os.path.exists("database.json"):
    try:
        with open("database.json", "r", encoding="utf-8") as f:
            old_list = json.load(f)
            for item in old_list:
                old_data_map[item["package"]] = item.get("rawInstalls", 0)
    except Exception:
        pass

new_database = []

# 3. Tarik Detail Metadata & Metrik Analisis
for pkg in discovered_packages:
    try:
        data = app(pkg, lang='en', country='us')
        
        current_installs = data.get('realInstalls', 0)
        previous_installs = old_data_map.get(pkg, current_installs)
        
        # Hitung pertumbuhan unduhan (Delta)
        recent_downloads = current_installs - previous_installs if current_installs >= previous_installs else 0
        
        new_database.append({
            "title": data.get('title', 'N/A'),
            "package": pkg,
            "category": data.get('genreId', 'OTHER'),
            "installsText": data.get('installs', '0+'),
            "rawInstalls": current_installs,
            "recentDownloads": recent_downloads,
            "releaseDate": data.get('released', 'N/A'),
            "score": round(data.get('score', 0) or 0, 1),
            "reviews": f"{data.get('reviews', 0):,}",
            "asoScore": min(100, int((data.get('score', 0) or 0) * 20))
        })
        print(f"✅ Teranalisis: {data.get('title')[:30]}...")
    except Exception:
        continue

# 4. Simpan ke database.json
with open("database.json", "w", encoding="utf-8") as f:
    json.dump(new_database, f, ensure_ascii=False, indent=4)

print("\n🚀 Analisis Pasar Selesai! Database V2 Siap Digunakan.")