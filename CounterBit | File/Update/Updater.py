import requests
import os

GITHUB_RAW = "https://raw.githubusercontent.com/Bruhrbx/CounterBit/main/CounterBit%20%7C%20File"
LOCAL_VERSION_FILE = "version.txt"
REMOTE_VERSION_URL = f"{GITHUB_RAW}/version.txt"

def get_local_version():
    if not os.path.exists(LOCAL_VERSION_FILE):
        return "0.0.0"
    with open(LOCAL_VERSION_FILE, "r") as f:
        return f.read().strip()

def get_remote_version():
    try:
        response = requests.get(REMOTE_VERSION_URL)
        if response.status_code == 200:
            return response.text.strip()
    except:
        return None

def download_file(path):
    url = f"{GITHUB_RAW}/{path}"
    local_path = os.path.join(".", path)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, "wb") as f:
        f.write(requests.get(url).content)

def update_all():
    print("🔄 Mengunduh versi terbaru...")
    files_to_update = [
        "client.py",
        "server.py",
        "version.txt",
        "sfx/Intro.mp3",
        "sfx/Pew.mp3",
        "sfx/Spawn.mp3",
        "sfx/Tada.mp3"
    ]
    for file in files_to_update:
        download_file(file)
        print(f"✅ Terupdate: {file}")
    print("✅ Update selesai!")

def main():
    print("📦 Mengecek update...")
    local = get_local_version()
    remote = get_remote_version()
    print(f"Versi Lokal : {local}")
    print(f"Versi Remote: {remote}")
    if remote and local != remote:
        print("🚀 Update tersedia!")
        update_all()
    else:
        print("👍 Sudah versi terbaru.")

if __name__ == "__main__":
    main()
