"""Ponto de entrada da API. Rodar com: uvicorn app.main:app --port 8000"""

from fastapi import FastAPI

from app.routes import router

app = FastAPI(
    title="API de Produtos – N3 Testes",
    description=(
        "CRUD de produtos usado nos testes unitários (pytest) "
        "e nos testes de carga (Grafana k6)."
    ),
    version="1.0.0",
)

app.include_router(router)
