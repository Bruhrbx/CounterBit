# =========================
# CounterBit Auto Installer + Auto Updater
# =========================

$baseFolder = "$env:USERPROFILE\Downloads\CounterBit"
New-Item -ItemType Directory -Force -Path $baseFolder | Out-Null
$baseURL = "https://raw.githubusercontent.com/Bruhrbx/CounterBit/main/CounterBit%20%7C%20File"

# == UNDUH FILE UTAMA ==
Write-Host "`n📦 Mengunduh file utama..." -ForegroundColor Cyan
Invoke-WebRequest "$baseURL/client.py" -OutFile "$baseFolder\client.py"
Invoke-WebRequest "$baseURL/server.py" -OutFile "$baseFolder/server.py"
Invoke-WebRequest "$baseURL/version.txt" -OutFile "$baseFolder\version.txt"

# == SFX ==
$sfxPath = "$baseFolder\sfx"
New-Item -ItemType Directory -Force -Path $sfxPath | Out-Null
Write-Host "`n🎧 Mengunduh suara..." -ForegroundColor Cyan
$sfxFiles = @("Intro.mp3", "Pew.mp3", "Spawn.mp3", "Tada.mp3", "Dial_Up.mp3")
foreach ($file in $sfxFiles) {
    Invoke-WebRequest "$baseURL/sfx/$file" -OutFile "$sfxPath\$file"
}

# == UPDATER FILE ==
$updatePath = "$baseFolder\Update"
New-Item -ItemType Directory -Force -Path $updatePath | Out-Null
Invoke-WebRequest "$baseURL/Update/Updater.py" -OutFile "$updatePath\Updater.py"

# == CEK PYTHON ==
function Check-Python {
    try {
        $ver = & python --version 2>&1
        if ($ver -match "Python") {
            Write-Host "`n✅ Python terdeteksi: $ver" -ForegroundColor Green
            return $true
        } else {
            return $false
        }
    } catch {
        Write-Host "`n❌ Python tidak ditemukan." -ForegroundColor Red
        return $false
    }
}
function Install-Python {
    Write-Host "`n🚀 Menginstal Python..." -ForegroundColor Yellow
    $installer = "$env:TEMP\python-installer.exe"
    Invoke-WebRequest "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe" -OutFile $installer
    Start-Process -Wait -FilePath $installer -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0"
    Remove-Item $installer
}
function Install-Pygame {
    Write-Host "`n🎮 Menginstal pygame..." -ForegroundColor Yellow
    pip install pygame
}

# == INSTALL PYTHON JIKA BELUM ==
if (-not (Check-Python)) {
    Install-Python
    $env:Path += ";C:\Program Files\Python312\Scripts;C:\Program Files\Python312\"
}
Install-Pygame

# == CEK VERSI ==
$localVer = Get-Content "$baseFolder\version.txt"
$remoteVer = Invoke-RestMethod "$baseURL/version.txt"

if ($localVer -ne $remoteVer) {
    $confirm = Read-Host "`n🔁 Versi baru tersedia ($remoteVer). Mau update ulang file? (y/n)"
    if ($confirm -eq "y") {
        Write-Host "`n⬇️  Mengunduh ulang file dari GitHub..." -ForegroundColor Cyan
        # Ulangi unduh ulang
        Invoke-WebRequest "$baseURL/client.py" -OutFile "$baseFolder/client.py"
        Invoke-WebRequest "$baseURL/server.py" -OutFile "$baseFolder/server.py"
        Invoke-WebRequest "$baseURL/version.txt" -OutFile "$baseFolder/version.txt"
        foreach ($file in $sfxFiles) {
            Invoke-WebRequest "$baseURL/sfx/$file" -OutFile "$sfxPath\$file"
        }
        Invoke-WebRequest "$baseURL/Update/Updater.py" -OutFile "$updatePath/Updater.py"
        Write-Host "`n✅ Update selesai ke versi $remoteVer!" -ForegroundColor Green
    } else {
        Write-Host "`n❎ Update dibatalkan." -ForegroundColor Yellow
    }
} else {
    Write-Host "`n🟢 Kamu sudah pakai versi terbaru ($localVer)" -ForegroundColor Green
}

# == SELESAI ==
Write-Host "`n✅ Semua proses selesai. Folder: $baseFolder" -ForegroundColor Green
Start-Process "explorer.exe" -ArgumentList "$baseFolder"
