param(
    [int[]]$Ports = @(8001, 8081, 8082, 19006)
)

$ErrorActionPreference = "Continue"

foreach ($Port in $Ports) {
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    $processIds = $connections | Select-Object -ExpandProperty OwningProcess -Unique

    foreach ($ProcessId in $processIds) {
        if (-not $ProcessId) {
            continue
        }

        $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        if ($null -eq $process) {
            continue
        }

        Write-Host "Parando porta $Port (PID $ProcessId - $($process.ProcessName))" -ForegroundColor Yellow
        Stop-Process -Id $ProcessId -Force
    }
}

Write-Host "Servicos encerrados nas portas configuradas." -ForegroundColor Cyan
