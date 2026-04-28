param(
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"
$VenvPython = Join-Path $RootDir ".venv\Scripts\python.exe"
$PythonExe = if (Test-Path $VenvPython) { $VenvPython } else { "python" }

Write-Host "== Factum / FactCheck-AI ==" -ForegroundColor Cyan
Write-Host "Raiz: $RootDir"

if (-not $SkipInstall) {
    Write-Host "`nInstalando dependencias do backend..." -ForegroundColor Cyan
    & $PythonExe -m pip install -r (Join-Path $BackendDir "requirements.txt")

    Write-Host "`nInstalando dependencias do frontend..." -ForegroundColor Cyan
    Push-Location $FrontendDir
    npm install
    Pop-Location
}

Write-Host "`nNormalizando dataset e garantindo modelo treinado..." -ForegroundColor Cyan
Push-Location $RootDir
& $PythonExe (Join-Path $RootDir "scripts\normalize_dataset.py")
& $PythonExe (Join-Path $RootDir "scripts\ensure_model.py")
Pop-Location

$BackendCommand = @"
Set-Location '$BackendDir'
`$env:PYTHONPATH='$BackendDir'
& '$PythonExe' -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
"@

$FrontendCommand = @"
Set-Location '$FrontendDir'
`$env:EXPO_PUBLIC_API_BASE_URL='http://127.0.0.1:8001'
npx.cmd expo start --web --port 8081
"@

Write-Host "`nIniciando backend em http://127.0.0.1:8001" -ForegroundColor Green
Start-Process powershell.exe -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $BackendCommand

Start-Sleep -Seconds 3

Write-Host "Iniciando frontend em http://localhost:8081" -ForegroundColor Green
Start-Process powershell.exe -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $FrontendCommand

Write-Host "`nPronto. Para parar os servicos, execute: ./parar_tudo.ps1" -ForegroundColor Cyan
