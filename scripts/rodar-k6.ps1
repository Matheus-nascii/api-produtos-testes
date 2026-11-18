# Roda os testes de carga do k6. Antes de cada teste a API é reiniciada (memória
# limpa) e, no fim, desligada. Para cada teste ficam em resultados\:
#   <teste>.html  relatório do painel web do k6, com gráficos
#   <teste>.txt   resumo que o k6 mostra no terminal
# e também maquina.txt (configuração do computador) e status-carga.txt.
#
# Uso: powershell -ExecutionPolicy Bypass -File scripts\rodar-k6.ps1                  (os três, ~22 min)
#      powershell -ExecutionPolicy Bypass -File scripts\rodar-k6.ps1 -Testes smoke     (só um)

param(
    [ValidateSet('smoke', 'average-load', 'stress')]
    [string[]]$Testes = @('smoke', 'average-load', 'stress')
)

[Console]::OutputEncoding = [Text.Encoding]::UTF8
$raiz = Split-Path $PSScriptRoot -Parent
Set-Location $raiz
$pastaResultados = Join-Path $raiz 'resultados'
New-Item -ItemType Directory -Force -Path $pastaResultados | Out-Null

$k6 = (Get-Command k6 -ErrorAction SilentlyContinue).Source
if (-not $k6 -and (Test-Path (Join-Path $env:ProgramFiles 'k6\k6.exe'))) {
    $k6 = Join-Path $env:ProgramFiles 'k6\k6.exe'
}
if (-not $k6) {
    Write-Host 'k6 não encontrado. Rode antes o 1-preparar-ambiente.bat.'
    exit 1
}
$py = Join-Path $raiz '.venv\Scripts\python.exe'
if (-not (Test-Path $py)) {
    Write-Host 'Ambiente não preparado. Rode antes o 1-preparar-ambiente.bat.'
    exit 1
}
if (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue) {
    Write-Host 'Já tem um programa usando a porta 8000 (a janela do 3-iniciar-api.bat?).'
    Write-Host 'Feche essa janela e rode este arquivo de novo.'
    exit 1
}

# Configuração do computador, para a análise dos resultados.
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$ram = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
@(
    "Data: $(Get-Date -Format 'dd/MM/yyyy HH:mm')",
    "Processador: $($cpu.Name.Trim()) ($($cpu.NumberOfCores) núcleos, $($cpu.NumberOfLogicalProcessors) threads)",
    "Memória RAM: $ram GB",
    "Sistema: $((Get-CimInstance Win32_OperatingSystem).Caption)",
    "Python: $((& $py --version 2>&1 | Out-String).Trim())",
    "k6: $((& $k6 version 2>&1 | Out-String).Trim())"
) | Out-File -Encoding utf8 (Join-Path $pastaResultados 'maquina.txt')

$status = Join-Path $pastaResultados 'status-carga.txt'
"Início: $(Get-Date -Format 'dd/MM/yyyy HH:mm')" | Out-File -Encoding utf8 $status

foreach ($teste in $Testes) {
    Write-Host ''
    Write-Host "=== $teste ==="
    Write-Host 'Reiniciando a API (memória limpa)...'
    $api = Start-Process -FilePath $py `
        -ArgumentList '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000', '--no-access-log' `
        -WorkingDirectory $raiz -WindowStyle Minimized -PassThru
    $pronta = $false
    for ($i = 0; $i -lt 30 -and -not $pronta; $i++) {
        try {
            Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 'http://127.0.0.1:8000/produtos' | Out-Null
            $pronta = $true
        }
        catch { Start-Sleep -Seconds 1 }
    }
    if (-not $pronta) {
        Write-Host 'A API não respondeu.'
        Stop-Process -Id $api.Id -Force -ErrorAction SilentlyContinue
        "${teste}: API_NAO_SUBIU" | Out-File -Append -Encoding utf8 $status
        exit 1
    }

    "${teste}: começou às $(Get-Date -Format 'HH:mm:ss')" | Out-File -Append -Encoding utf8 $status
    $env:K6_WEB_DASHBOARD = 'true'
    $env:K6_WEB_DASHBOARD_EXPORT = Join-Path $pastaResultados "$teste.html"
    & $k6 run --no-color (Join-Path $raiz "k6\$teste.js") | Tee-Object -Variable saida
    $codigo = $LASTEXITCODE
    $saida | Out-File -Encoding utf8 (Join-Path $pastaResultados "$teste.txt")
    "${teste}: terminou às $(Get-Date -Format 'HH:mm:ss') com código $codigo (0 = thresholds aprovados; 99 = algum threshold reprovado)" |
        Out-File -Append -Encoding utf8 $status

    Stop-Process -Id $api.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
}

'CARGA_OK' | Out-File -Append -Encoding utf8 $status
Write-Host ''
Write-Host 'Pronto. Relatórios em resultados\'
