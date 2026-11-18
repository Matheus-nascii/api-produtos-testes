# Prepara o ambiente no Windows: confere o Python, cria o .venv, instala as
# bibliotecas do requirements.txt e instala o k6 (pelo winget) se ele não existir.
# O registro fica em resultados\preparar.txt.

[Console]::OutputEncoding = [Text.Encoding]::UTF8
$raiz = Split-Path $PSScriptRoot -Parent
Set-Location $raiz
New-Item -ItemType Directory -Force -Path resultados | Out-Null
$log = Join-Path $raiz 'resultados\preparar.txt'
Set-Content -Path $log -Value "Preparação iniciada em $(Get-Date -Format 'dd/MM/yyyy HH:mm')" -Encoding utf8

function Registrar([string]$texto) {
    Write-Host $texto
    Add-Content -Path $log -Value $texto -Encoding utf8
}

# 1. Python (instala o 3.12 pelo winget, só para este usuário, se não houver)
$script:pyExe = $null
$script:pyArgs = @()
function Achar-Python {
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) { $script:pyExe = $launcher.Source; $script:pyArgs = @('-3'); return }
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python -and $python.Source -notlike '*WindowsApps*') { $script:pyExe = $python.Source; return }
    foreach ($v in '313', '312', '311', '310') {
        foreach ($base in @((Join-Path $env:LOCALAPPDATA 'Programs\Python'), $env:ProgramFiles)) {
            $candidato = Join-Path $base "Python$v\python.exe"
            if (Test-Path $candidato) { $script:pyExe = $candidato; return }
        }
    }
}
Achar-Python
if (-not $script:pyExe) {
    Registrar 'Python não encontrado. Instalando o Python 3.12 com o winget (1 a 3 minutos)...'
    $saida = winget install --id Python.Python.3.12 -e --source winget --scope user --silent `
        --accept-package-agreements --accept-source-agreements 2>&1 | Out-String
    Add-Content -Path $log -Value $saida -Encoding utf8
    Achar-Python
}
if (-not $script:pyExe) {
    Registrar 'PYTHON_NAO_ENCONTRADO: instale o Python 3.10 ou mais novo em https://www.python.org/downloads/ marcando "Add python.exe to PATH", e rode este arquivo de novo.'
    exit 1
}
$pyExe = $script:pyExe
$pyArgs = $script:pyArgs
$versao = (& $pyExe @pyArgs --version 2>&1 | Out-String).Trim()
Registrar "Python encontrado: $versao"

# 2. Ambiente virtual e bibliotecas
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    Registrar 'Criando o ambiente virtual (.venv)...'
    & $pyExe @pyArgs -m venv .venv
}
$venvPy = Join-Path $raiz '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPy)) {
    Registrar 'ERRO_VENV: não foi possível criar o ambiente virtual.'
    exit 1
}
Registrar 'Instalando FastAPI, Uvicorn, pytest, pytest-cov e httpx (pode levar 1 a 2 minutos)...'
$saida = & $venvPy -m pip install --disable-pip-version-check -r requirements.txt 2>&1 | Out-String
$codigoPip = $LASTEXITCODE
Add-Content -Path $log -Value $saida -Encoding utf8
if ($codigoPip -ne 0) {
    Registrar 'ERRO_PIP: a instalação das bibliotecas falhou (detalhes acima).'
    exit 1
}
$pacotes = & $venvPy -m pip list --format=freeze 2>&1 |
    Select-String -Pattern '^(fastapi|uvicorn|pydantic|pytest|pytest-cov|httpx)=='
Registrar ('Bibliotecas: ' + (($pacotes | ForEach-Object { $_.Line }) -join ', '))

# 3. k6
function Achar-K6 {
    $cmd = Get-Command k6 -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $padrao = Join-Path $env:ProgramFiles 'k6\k6.exe'
    if (Test-Path $padrao) { return $padrao }
    return $null
}
$k6 = Achar-K6
if (-not $k6) {
    Registrar 'Instalando o k6 com o winget (se o Windows pedir permissão, clique em Sim)...'
    $saida = winget install k6 --source winget --accept-package-agreements --accept-source-agreements 2>&1 | Out-String
    Add-Content -Path $log -Value $saida -Encoding utf8
    $k6 = Achar-K6
}
if (-not $k6) {
    Registrar 'K6_NAO_ENCONTRADO: instale o k6 manualmente (https://grafana.com/docs/k6/latest/set-up/install-k6/) e rode este arquivo de novo.'
    exit 1
}
Registrar ('k6: ' + (& $k6 version 2>&1 | Out-String).Trim())
Registrar 'PREPARAR_OK'
