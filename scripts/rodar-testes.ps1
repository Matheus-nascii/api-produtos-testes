# Roda os testes unitários com cobertura e salva a saída em resultados\pytest.txt.
# O relatório HTML da cobertura fica em htmlcov\index.html.
# Uso: powershell -ExecutionPolicy Bypass -File scripts\rodar-testes.ps1

[Console]::OutputEncoding = [Text.Encoding]::UTF8
$env:PYTHONUTF8 = '1'
$raiz = Split-Path $PSScriptRoot -Parent
Set-Location $raiz
New-Item -ItemType Directory -Force -Path resultados | Out-Null

$py = Join-Path $raiz '.venv\Scripts\python.exe'
if (-not (Test-Path $py)) {
    Write-Host 'Ambiente não preparado. Rode antes o 1-preparar-ambiente.bat.'
    exit 1
}

& $py -m pytest -v --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=90 |
    Tee-Object -Variable saida
$codigo = $LASTEXITCODE
$saida | Out-File -Encoding utf8 (Join-Path $raiz 'resultados\pytest.txt')
Write-Host ''
Write-Host 'Relatório HTML da cobertura: htmlcov\index.html'
exit $codigo
