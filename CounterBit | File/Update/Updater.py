import os
import urllib.request

# Tentukan path instalasi CounterBit
base_folder = os.path.join(os.path.expanduser("~"), "Downloads", "CounterBit")
sfx_folder = os.path.join(base_folder, "sfx")
update_folder = os.path.join(base_folder, "Update")

# URL GitHub
base_url = "https://raw.githubusercontent.com/Bruhrbx/CounterBit/main/CounterBit%20%7C%20File"

# File utama yang perlu diunduh
main_files = {
    "client.py": os.path.join(base_folder, "client.py"),
    "server.py": os.path.join(base_folder, "server.py"),
    "version.txt": os.path.join(base_folder, "version.txt"),
    "Update/Updater.py": os.path.join(update_folder, "Updater.py")
}

# File sfx yang perlu diunduh
sfx_files = ["Intro.mp3", "Pew.mp3", "Spawn.mp3", "Tada.mp3"]

# Pastikan folder ada
os.makedirs(base_folder, exist_ok=True)
os.makedirs(sfx_folder, exist_ok=True)
os.makedirs(update_folder, exist_ok=True)

def download_file(url, dest):
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"[✓] {os.path.basename(dest)} berhasil diunduh")
    except Exception as e:
        print(f"[X] Gagal mengunduh {url} -> {e}")

# Unduh file utama
print("📥 Mengunduh file utama:")
for filename, path in main_files.items():
    download_file(f"{base_url}/{filename}", path)

# Unduh file sfx
print("\n🎧 Mengunduh file suara:")
for sfx in sfx_files:
    sfx_url = f"{base_url}/sfx/{sfx}"
    sfx_dest = os.path.join(sfx_folder, sfx)
    download_file(sfx_url, sfx_dest)

print("\n✅ Update selesai. Semua file disimpan di:")
print(base_folder)

