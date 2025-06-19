$baseFolder = "$env:USERPROFILE\Downloads\CounterBit"
New-Item -ItemType Directory -Force -Path $baseFolder | Out-Null

$baseURL = "https://raw.githubusercontent.com/Bruhrbx/CounterBit/main/CounterBit%20%7C%20File"

Write-Host "`n📦 Mengunduh file utama..." -ForegroundColor Cyan
Invoke-WebRequest "$baseURL/client.py" -OutFile "$baseFolder\client.py"
Invoke-WebRequest "$baseURL/server.py" -OutFile "$baseFolder\server.py"

# Buat folder Sfx
$sfxPath = "$baseFolder\Sfx"
New-Item -ItemType Directory -Force -Path $sfxPath | Out-Null

Write-Host "`n🎧 Mengunduh suara ke folder Sfx..." -ForegroundColor Cyan
Invoke-WebRequest "$baseURL/Sfx/Intro.mp3" -OutFile "$sfxPath\Intro.mp3"
Invoke-WebRequest "$baseURL/Sfx/Pew.mp3" -OutFile "$sfxPath\Pew.mp3"
Invoke-WebRequest "$baseURL/Sfx/Spawn.mp3" -OutFile "$sfxPath\Spawn.mp3"
Invoke-WebRequest "$baseURL/Sfx/Tada!.mp3" -OutFile "$sfxPath\Tada!.mp3"

# Cek dan install Python jika belum ada
function Check-Python {
    try {
        $ver = & python --version 2>&1
        return $ver -match "Python"
    } catch {
        return $false
    }
}
function Install-Python {
    Write-Host "`n🚀 Menginstal Python..." -ForegroundColor Yellow
    $pythonInstaller = "$env:TEMP\python-installer.exe"
    Invoke-WebRequest "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe" -OutFile $pythonInstaller
    Start-Process -Wait -FilePath $pythonInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0"
    Remove-Item $pythonInstaller
}
function Install-Pygame {
    Write-Host "`n🎮 Menginstal Pygame..." -ForegroundColor Yellow
    pip install pygame
}

if (-not (Check-Python)) {
    Install-Python
    $env:Path += ";C:\Program Files\Python312\Scripts;C:\Program Files\Python312\"
}

Install-Pygame

Write-Host "`n✅ File berhasil diinstal di: $baseFolder" -ForegroundColor Green
Start-Process "explorer.exe" "$baseFolder"


# Install Pygame
Install-Pygame

# Buka folder hasil ekstrak
Write-Host "`n✅ Selesai! File telah di-ekstrak ke:`n$targetFolder" -ForegroundColor Green
Start-Process "explorer.exe" "$targetFolder"
