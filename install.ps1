# install.ps1 — One-click setup script for Windows
# Run this script from the repository root: .\install.ps1

Write-Host "==========================================================" -ForegroundColor Purple
Write-Host "   Psycho503 Dev AI Agency - Setup Installer (Windows)" -ForegroundColor Purple
Write-Host "==========================================================" -ForegroundColor Purple

# 1. Check Python version
$python_cmd = "python"
if (!(Get-Command $python_cmd -ErrorAction SilentlyContinue)) {
    $python_cmd = "py"
    if (!(Get-Command $python_cmd -ErrorAction SilentlyContinue)) {
        Write-Error "Python no encontrado. Por favor, instala Python 3.9 o superior desde https://python.org"
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

# 3. Upgrade pip and install ALL dependencies (including test suite)
Write-Host "Instalando dependencias de produccion y testing..." -ForegroundColor Cyan
& .venv\Scripts\python.exe -m pip install --upgrade pip
& .venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Error "Error al instalar las dependencias."
    exit 1
}
Write-Host "Dependencias instaladas con exito." -ForegroundColor Green

# 4. Environment File Setup
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "Copiando .env.example a .env..." -ForegroundColor Cyan
        Copy-Item ".env.example" ".env"
        Write-Host "IMPORTANTE: Abre .env y configura tu API Key antes de continuar." -ForegroundColor Yellow
    } else {
        New-Item ".env" -ItemType File | Out-Null
    }
} else {
    Write-Host "Archivo .env ya existe." -ForegroundColor Green
}

# 5. Run the test suite to verify the install is healthy
Write-Host ""
Write-Host "Verificando instalacion con suite de tests..." -ForegroundColor Cyan
& .venv\Scripts\python.exe -m pytest tests/runtime/ -q --tb=short 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ADVERTENCIA: Algunos tests fallaron. Revisa los errores antes de usar en produccion." -ForegroundColor Yellow
} else {
    Write-Host "Todos los tests pasaron. El sistema esta listo." -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Purple
Write-Host "Instalacion completada." -ForegroundColor Green
Write-Host ""
Write-Host "PROXIMOS PASOS:" -ForegroundColor White
Write-Host "  1. Edita .env con tu API Key (OPENAI_API_KEY o NVIDIA_API_KEY)" -ForegroundColor Yellow
Write-Host "  2. Abre el Dashboard en tu navegador: http://localhost:8050" -ForegroundColor Yellow
Write-Host "  3. Ejecuta la agencia: .venv\Scripts\python.exe setup.py --run" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Purple
