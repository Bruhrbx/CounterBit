$targetFolder = "$env:USERPROFILE\Downloads\CounterBit"
$zipPath = "$env:TEMP\CounterBit.zip"
$zipURL = "https://raw.githubusercontent.com/Bruhrbx/CounterBit/main/CounterBit.zip"

function Check-Python {
    try {
        $pyVersion = & python --version 2>&1
        if ($pyVersion -match "Python") {
            return $true
        }
    } catch {
        return $false
    }
    return $false
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

# ===== MULAI =====
Write-Host "`n📦 Mengunduh CounterBit.zip..." -ForegroundColor Cyan
Invoke-WebRequest $zipURL -OutFile $zipPath

Write-Host "`n📂 Mengekstrak ke $targetFolder..." -ForegroundColor Cyan
Expand-Archive -LiteralPath $zipPath -DestinationPath $targetFolder -Force
Remove-Item $zipPath

# Install Python jika belum ada
if (-not (Check-Python)) {
    Install-Python
    $env:Path += ";C:\Program Files\Python312\Scripts;C:\Program Files\Python312\"
}

# Install Pygame
Install-Pygame

# Buka folder hasil ekstrak
Write-Host "`n✅ Selesai! File telah di-ekstrak ke:`n$targetFolder" -ForegroundColor Green
Start-Process "explorer.exe" "$targetFolder"
