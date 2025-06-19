# =======================
# CounterBit Updater.ps1
# =======================

# Path lokal & URL
$baseFolder = "$env:USERPROFILE\Downloads\CounterBit"
$localVersionFile = "$baseFolder\version.txt"
$baseURL = "https://raw.githubusercontent.com/Bruhrbx/CounterBit/main/CounterBit%20%7C%20File"
$remoteVersionURL = "$baseURL/version.txt"

# Cek apakah folder CounterBit ada
if (!(Test-Path $baseFolder)) {
    Write-Host "`n❌ Folder CounterBit tidak ditemukan. Jalankan install.ps1 dulu!" -ForegroundColor Red
    exit
}

# Ambil versi lokal
if (Test-Path $localVersionFile) {
    $localVersion = Get-Content $localVersionFile
} else {
    $localVersion = "0.0.0"
}

# Ambil versi terbaru dari GitHub
try {
    $remoteVersion = Invoke-RestMethod $remoteVersionURL
} catch {
    Write-Host "`n❌ Gagal mengambil versi dari GitHub." -ForegroundColor Red
    exit
}

Write-Host "`n📦 Versi saat ini: $localVersion"
Write-Host "🌐 Versi terbaru : $remoteVersion"

# Bandingkan versi
if ($localVersion -ne $remoteVersion) {
    $choice = Read-Host "`n🔁 Versi baru tersedia. Mau update ke versi $remoteVersion? (y/n)"
    if ($choice -eq "y") {
        Write-Host "`n⬇️  Updating... (version $remoteVersion)" -ForegroundColor Cyan

        # Unduh file utama
        Invoke-WebRequest "$baseURL/client.py" -OutFile "$baseFolder\client.py"
        Invoke-WebRequest "$baseURL/server.py" -OutFile "$baseFolder/server.py"
        Invoke-WebRequest "$baseURL/version.txt" -OutFile "$baseFolder/version.txt"

        # Update SFX
        $sfxPath = "$baseFolder\sfx"
        if (!(Test-Path $sfxPath)) {
            New-Item -ItemType Directory -Path $sfxPath | Out-Null
        }

        $sfxFiles = @("Intro.mp3", "Pew.mp3", "Spawn.mp3", "Tada.mp3")
        foreach ($file in $sfxFiles) {
            Invoke-WebRequest "$baseURL/sfx/$file" -OutFile "$sfxPath\$file"
        }

        # Update Updater.py
        $updatePath = "$baseFolder\Update"
        if (!(Test-Path $updatePath)) {
            New-Item -ItemType Directory -Path $updatePath | Out-Null
        }
        Invoke-WebRequest "$baseURL/Update/Updater.py" -OutFile "$updatePath\Updater.py"

        Write-Host "`n✅ Update selesai ke versi $remoteVersion!" -ForegroundColor Green
    } else {
        Write-Host "`n❎ Update dibatalkan." -ForegroundColor Yellow
    }
} else {
    Write-Host "`n🟢 Kamu sudah menggunakan versi terbaru ($localVersion)" -ForegroundColor Green
}
