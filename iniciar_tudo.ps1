$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $projectRoot "backend"
$frontendPath = Join-Path $projectRoot "frontend"

$pythonExe = "c:/python314/python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

$backendCmd = "Set-Location '$backendPath'; $pythonExe -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload"
$frontendCmd = "Set-Location '$frontendPath'; `$env:EXPO_PUBLIC_API_BASE_URL='http://127.0.0.1:8001'; npx.cmd expo start --web --port 8081"

Start-Process powershell -ArgumentList @('-NoExit', '-Command', $backendCmd)
Start-Process powershell -ArgumentList @('-NoExit', '-Command', $frontendCmd)

Write-Host "Backend iniciando em: http://127.0.0.1:8001"
Write-Host "Frontend iniciando em: http://localhost:8081"
Write-Host "Aguarde alguns segundos e abra a URL do frontend no navegador."
