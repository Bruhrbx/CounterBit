# =========================
# CounterBit Auto Installer
# =========================

# Lokasi folder tujuan
$baseFolder = "$env:USERPROFILE\Downloads\CounterBit"
New-Item -ItemType Directory -Force -Path $baseFolder | Out-Null

# Base URL GitHub raw
$baseURL = "https://raw.githubusercontent.com/Bruhrbx/CounterBit/main/CounterBit%20%7C%20File"

# == FILE UTAMA ==
Write-Host "`n📦 Mengunduh file utama..." -ForegroundColor Cyan
Invoke-WebRequest "$baseURL/client.py" -OutFile "$baseFolder\client.py"
Invoke-WebRequest "$baseURL/server.py" -OutFile "$baseFolder/server.py"
Invoke-WebRequest "$baseURL/version.txt" -OutFile "$baseFolder/version.txt"

# == FOLDER SFX ==
$sfxPath = "$baseFolder\sfx"
New-Item -ItemType Directory -Force -Path $sfxPath | Out-Null

Write-Host "`n🎧 Mengunduh suara ke folder sfx..." -ForegroundColor Cyan
$sfxFiles = @("Intro.mp3", "Pew.mp3", "Spawn.mp3", "Tada.mp3")
foreach ($file in $sfxFiles) {
    Invoke-WebRequest "$baseURL/sfx/$file" -OutFile "$sfxPath\$file"
    Write-Host "  ✔ $file"
}

# == FOLDER UPDATE ==
$updatePath = "$baseFolder\Update"
New-Item -ItemType Directory -Force -Path $updatePath | Out-Null

Write-Host "`n⚙️ Mengunduh updater..." -ForegroundColor Cyan
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

# == INSTALL PYTHON ==
function Install-Python {
    Write-Host "`n🚀 Menginstal Python 3.12.3..." -ForegroundColor Yellow
    $installer = "$env:TEMP\python-installer.exe"
    Invoke-WebRequest "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe" -OutFile $installer
    Start-Process -Wait -FilePath $installer -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0"
    Remove-Item $installer
    Write-Host "✅ Python berhasil diinstal!" -ForegroundColor Green
}

# == INSTALL PYGAME ==
function Install-Pygame {
    Write-Host "`n🎮 Menginstal pygame..." -ForegroundColor Yellow
    pip install pygame
}

# == EKSEKUSI ==
if (-not (Check-Python)) {
    Install-Python
    $env:Path += ";C:\Program Files\Python312\Scripts;C:\Program Files\Python312\"
}
Install-Pygame

# == SELESAI ==
Write-Host "`n✅ Semua file sudah berhasil diunduh ke: $baseFolder" -ForegroundColor Green
Start-Process "explorer.exe" -ArgumentList "$baseFolder"
t-Process "explorer.exe" -ArgumentList "$baseFolder"
