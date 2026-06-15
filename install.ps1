# install.ps1 — One-click setup script for Windows

Write-Host "==========================================================" -ForegroundColor Purple
Write-Host "   🤖 Psycho503 Dev AI Agency — Setup Installer (Windows)" -ForegroundColor Purple
Write-Host "==========================================================" -ForegroundColor Purple

# 1. Check Python version
$python_cmd = "python"
if (!(Get-Command $python_cmd -ErrorAction SilentlyContinue)) {
    $python_cmd = "py"
    if (!(Get-Command $python_cmd -ErrorAction SilentlyContinue)) {
        Write-Error "Python no encontrado. Por favor, instala Python 3.9 o superior primero."
        exit 1
    }
}

$pyVersion = & $python_cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Host "Python detectado: v$pyVersion" -ForegroundColor Green

# 2. Create Virtual Environment
if (!(Test-Path ".venv")) {
    Write-Host "Creando entorno virtual .venv..." -ForegroundColor Cyan
    & $python_cmd -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Error al crear el entorno virtual."
        exit 1
    }
} else {
    Write-Host "Entorno virtual .venv existente encontrado." -ForegroundColor Green
}

# 3. Upgrade pip and install dependencies
Write-Host "Actualizando pip e instalando dependencias..." -ForegroundColor Cyan
& .venv\Scripts\python.exe -m pip install --upgrade pip
& .venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Error "Error al instalar las dependencias."
    exit 1
}
Write-Host "Dependencias instaladas con éxito." -ForegroundColor Green

# 4. Environment File Setup
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "Copiando .env.example a .env..." -ForegroundColor Cyan
        Copy-Item ".env.example" ".env"
    } else {
        Write-Host "Creando archivo .env vacío..." -ForegroundColor Cyan
        New-Item ".env" -ItemType File | Out-Null
    }
}

Write-Host "==========================================================" -ForegroundColor Purple
Write-Host "✅ Instalación completada con éxito." -ForegroundColor Green
Write-Host "Para iniciar el asistente de configuración interactivo ejecuta:" -ForegroundColor White
Write-Host "  .venv\Scripts\python.exe setup.py" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Purple
