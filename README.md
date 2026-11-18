# N3 – Testes: API de Produtos

API REST em Python (FastAPI) com um CRUD de produtos, testes unitários com pytest
(cobertura mínima de 90%) e testes de carga com o Grafana k6 (Smoke, Average Load e Stress).

## Requisitos

- Python 3.10 ou mais novo
- Grafana k6 (no Windows: `winget install k6 --source winget`; outras formas em
  https://grafana.com/docs/k6/latest/set-up/install-k6/)

## Atalhos no Windows

Na pasta do projeto, dê dois cliques, nesta ordem:

| Arquivo | O que faz |
| --- | --- |
| `1-preparar-ambiente.bat` | Cria o `.venv`, instala as bibliotecas e o k6 (se faltar) |
| `2-testes-unitarios.bat` | Roda o pytest com cobertura e gera `htmlcov/index.html` |
| `3-iniciar-api.bat` | Liga a API em http://localhost:8000 (Swagger em `/docs`) |
| `4-testes-de-carga.bat` | Roda Smoke, Average Load e Stress (~22 min), reiniciando a API antes de cada um |
| `5-gravar-telas.bat` | Grava prints do CRUD no Swagger em `resultados/telas/` (para o vídeo) |
| `6-rodar-so-o-stress.bat` | Roda só o Stress Test (~11 min) |

Feche a janela do `3-iniciar-api.bat` antes de rodar o `4-testes-de-carga.bat`.
Os comandos equivalentes estão nas seções abaixo.

## Configurar o ambiente

Windows (PowerShell), dentro da pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Se o PowerShell bloquear o `Activate.ps1`, rode antes
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

Linux ou macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Rodar a API

```powershell
uvicorn app.main:app --port 8000
```

A documentação interativa (Swagger) fica em http://localhost:8000/docs.
A API roda com um único processo de propósito: os dados ficam em memória e não seriam
compartilhados entre vários processos.

### Endpoints

| Método | Rota | O que faz | Respostas |
| --- | --- | --- | --- |
| POST | /produtos | Cria um produto | 201 criado · 422 dados inválidos |
| GET | /produtos | Lista todos | 200 |
| GET | /produtos/{id} | Busca um | 200 · 404 não encontrado |
| PUT | /produtos/{id} | Atualiza um | 200 · 404 · 422 |
| DELETE | /produtos/{id} | Exclui um | 204 · 404 |

Regras de validação: `nome` com 3 a 100 caracteres, `preco` maior que 0 e `estoque`
inteiro, 0 ou mais. Dados inválidos retornam 422 (padrão do FastAPI para JSON bem formado
com dados que violam as regras).

## Testes unitários e cobertura

```powershell
python -m pytest -v --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=90
```

- `tests/test_schemas.py`: regras de validação, sem HTTP.
- `tests/test_repository.py`: armazenamento em memória, sem HTTP.
- `tests/test_routes.py`: cada endpoint com o TestClient do FastAPI, sem subir servidor.

Os testes cobrem cenários de sucesso, falha (produto inexistente) e validação de dados.
O relatório HTML da cobertura fica em `htmlcov/index.html`. A execução falha se a
cobertura ficar abaixo de 90%.

## Testes de carga (k6)

O script abaixo liga a API, roda o teste, desliga a API e repete para o próximo, para
cada teste começar com a memória limpa:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\rodar-k6.ps1                       # os três
powershell -ExecutionPolicy Bypass -File scripts\rodar-k6.ps1 -Testes smoke         # só um
```

Ele liga o painel web do k6 e salva em `resultados/` o relatório HTML (`<teste>.html`) e o
resumo do terminal (`<teste>.txt`) de cada teste, além da configuração do computador
(`maquina.txt`). Para rodar um teste à mão, com a API já ligada: `k6 run k6/smoke.js`.
A API dos testes de carga roda com `--no-access-log`: escrever uma linha de log por
requisição no console do Windows deixaria a própria API mais lenta.

Os três testes usam o mesmo fluxo (`k6/fluxo.js`): cada usuário virtual cria um produto,
lista todos, busca o criado, atualiza, exclui e espera 1 segundo. Toda resposta tem um
`check` do código esperado.

| Teste | Usuários virtuais | Duração | Thresholds |
| --- | --- | --- | --- |
| Smoke | 2 | 1 min | falhas < 1% · p95 < 300 ms · checks > 99% |
| Average Load | sobe até 50 | 8 min (2 subindo, 5 mantendo, 1 descendo) | falhas < 1% · p95 < 500 ms · checks > 99% |
| Stress | sobe em degraus até 600 | 11 min (200, 400 e 600, mantendo cada nível, e desce) | falhas < 5% · p95 < 1000 ms · checks > 95% |

Para resultados comparáveis: rode sempre no mesmo computador, com o carregador ligado e
outros programas fechados, e reinicie a API antes de cada teste.

## Resultados obtidos (18/11/2026)

Executados num notebook com Intel Core i5-13420H (8 núcleos, 12 threads), 7,7 GB de RAM,
Windows 11, Python 3.12.10 e k6 v2.4.0. A API e o k6 rodaram na mesma máquina e disputaram
o processador. As saídas completas estão em `resultados/`.

**Testes unitários:** 47 testes passando, cobertura de 100% das linhas (`resultados/pytest.txt`
e `htmlcov/index.html`).

| Teste | Usuários (máx.) | Requisições | Req/s (média) | p95 | Falhas | Thresholds |
| --- | --- | --- | --- | --- | --- | --- |
| Smoke | 2 | 600 | 9,9 | 2,84 ms | 0% | aprovados |
| Average Load | 50 | 96.840 | 201,5 | 4,8 ms | 0% | aprovados |
| Stress | 600 | 1.146.080 | 1.735 | 5,89 ms | 0% | aprovados |

**Stress, por degrau** (mediana dos períodos de 10 s): 200 usuários, cerca de 993 req/s e p95 de
4,43 ms; 400 usuários, 1.990 req/s e 5,49 ms; 600 usuários, 2.969 req/s e 4,60 ms. No fim do
patamar de 600, por cerca de 20 s, o p95 subiu para 416 ms e a vazão caiu para 1.642 req/s, sem
nenhuma falha; a API se recuperou quando a carga começou a cair. Uma primeira versão do Stress,
só até 200 usuários (`resultados/stress-200usuarios.*`), não mostrou degradação (p95 de 3,79 ms).

**Gargalos prováveis e melhorias:** a API roda num único processo (melhoria: vários workers,
o que exige um banco de dados no lugar da memória); `GET /produtos` não tem paginação (no pico,
os dados recebidos quintuplicaram, sinal de listas maiores); e a API e o k6 dividiram o mesmo
processador (melhoria: rodar o k6 em outro computador).

## Estrutura

```text
app/        API (main.py, routes.py, schemas.py, repository.py)
tests/      testes unitários
k6/         scripts dos testes de carga
scripts/    atalhos em PowerShell para rodar testes e k6
resultados/ relatórios e saídas das execuções
```
