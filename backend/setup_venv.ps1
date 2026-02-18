<#
setup_venv.ps1

Creates a fresh virtual environment, installs requirements, and starts uvicorn.
Run from the backend folder (PowerShell) with: `.ackend\setup_venv.ps1`

If you already have a working `venv` you can pass a name: `.ackend\setup_venv.ps1 -EnvName venv`
#>

param(
    [string]$EnvName = "env_auto",
    [switch]$ForceRecreate
)

try {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
    Set-Location $scriptDir
    Write-Host "Working directory: $scriptDir"

    if (Test-Path $EnvName) {
        if ($ForceRecreate) {
            Write-Host "Removing existing virtual environment '$EnvName'..."
            Remove-Item -LiteralPath $EnvName -Recurse -Force -ErrorAction SilentlyContinue
        } else {
            Write-Host "Virtual environment '$EnvName' already exists. Using it. Use -ForceRecreate to recreate."
        }
    }

    if (-not (Test-Path $EnvName)) {
        Write-Host "Creating virtual environment: $EnvName"
        python -m venv $EnvName
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment. Ensure 'python' is on PATH and is version 3.8+"
        }
    }

    $venvPython = Join-Path $EnvName "Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        throw "Virtual environment python not found at $venvPython. Activation failed or venv corrupted."
    }

    Write-Host "Upgrading pip in venv..."
    & $venvPython -m pip install --upgrade pip

    Write-Host "Installing requirements from requirements.txt"
    & $venvPython -m pip install -r requirements.txt

    Write-Host "Starting Uvicorn with venv Python..."
    & $venvPython -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    Write-Host "If files are locked, try closing running Python processes or reboot then re-run this script." -ForegroundColor Yellow
    exit 1
}
