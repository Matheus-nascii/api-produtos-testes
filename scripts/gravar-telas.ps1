# Instala o Playwright (só para gravar as telas do vídeo) e roda scripts\gravar_telas.py.
# A saída fica em resultados\telas\ e o registro em resultados\telas\log.txt.

[Console]::OutputEncoding = [Text.Encoding]::UTF8
$env:PYTHONUTF8 = '1'
$raiz = Split-Path $PSScriptRoot -Parent
Set-Location $raiz
$py = Join-Path $raiz '.venv\Scripts\python.exe'
if (-not (Test-Path $py)) {
    Write-Host 'Ambiente não preparado. Rode antes o 1-preparar-ambiente.bat.'
    exit 1
}
$pasta = Join-Path $raiz 'resultados\telas'
New-Item -ItemType Directory -Force -Path $pasta | Out-Null
$log = Join-Path $pasta 'log.txt'

& $py -c "import playwright" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Instalando o Playwright (1 vez só)...'
    & $py -m pip install --disable-pip-version-check playwright 2>&1 | Out-String | Out-File -Encoding utf8 $log
}

& $py (Join-Path $raiz 'scripts\gravar_telas.py') 2>&1 | Tee-Object -Variable saida
$codigo = $LASTEXITCODE
$saida | Out-File -Append -Encoding utf8 $log

if ($codigo -ne 0 -and ($saida | Out-String) -match "Executable doesn't exist|playwright install") {
    Write-Host 'Baixando o navegador do Playwright (cerca de 150 MB)...'
    & $py -m playwright install chromium ffmpeg 2>&1 | Out-String | Out-File -Append -Encoding utf8 $log
    & $py (Join-Path $raiz 'scripts\gravar_telas.py') 2>&1 | Tee-Object -Variable saida
    $codigo = $LASTEXITCODE
    $saida | Out-File -Append -Encoding utf8 $log
}
exit $codigo
