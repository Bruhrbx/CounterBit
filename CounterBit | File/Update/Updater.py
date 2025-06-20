import os
import urllib.request

# Lokasi file versi lokal
base_folder = os.path.join(os.path.expanduser("~"), "Downloads", "CounterBit")
version_file_local = os.path.join(base_folder, "version.txt")

# Lokasi file versi di GitHub (RAW URL, bukan HTML biasa)
version_url_remote = "https://raw.githubusercontent.com/Bruhrbx/CounterBit/main/CounterBit%20%7C%20File/version.txt"

def get_local_version():
    try:
        with open(version_file_local, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "0.0.0"  # Jika file tidak ada, anggap versi sangat lama

def get_remote_version():
    try:
        with urllib.request.urlopen(version_url_remote) as response:
            return response.read().decode().strip()
    except Exception as e:
        print(f"[X] Gagal mengambil versi terbaru dari GitHub: {e}")
        return None

# Ambil versi
versi_sekarang = get_local_version()
versi_terbaru = get_remote_version()

# Tampilkan perbandingan versi
print("Versi Sekarang        Versi Terbaru")
print(f"     v{versi_sekarang}      ------>      v{versi_terbaru}\n")

# Cek apakah perlu update
if versi_terbaru is None:
    exit()

if versi_sekarang == versi_terbaru:
    print("✅ Punya kamu sudah Versi Lebih Baru")
    exit()

# Jika versi beda, tanya user
jawaban = input(f"Ada versi baru v{versi_terbaru}. Mau update? (y/n): ").lower()
if jawaban != "y":
    print("❌ Update dibatalkan.")
    exit()

# ------------------ PROSES UPDATE ------------------

# Folder tambahan
sfx_folder = os.path.join(base_folder, "sfx")
update_folder = os.path.join(base_folder, "Update")

# URL base GitHub
base_url = "https://raw.githubusercontent.com/Bruhrbx/CounterBit/main/CounterBit%20%7C%20File"

# File utama
main_files = {
    "client.py": os.path.join(base_folder, "client.py"),
    "server.py": os.path.join(base_folder, "server.py"),
    "version.txt": os.path.join(base_folder, "version.txt"),
    "Update/Updater.py": os.path.join(update_folder, "Updater.py")
}

# File suara
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
print("\n📥 Mengunduh file utama:")
for filename, path in main_files.items():
    download_file(f"{base_url}/{filename}", path)

# Unduh suara
print("\n🎧 Mengunduh file suara:")
for sfx in sfx_files:
    sfx_url = f"{base_url}/sfx/{sfx}"
    sfx_dest = os.path.join(sfx_folder, sfx)
    download_file(sfx_url, sfx_dest)

print("\n✅ Update selesai. Semua file disimpan di:")
print(base_folder)
