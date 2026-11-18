"""Testes de cada endpoint com o TestClient do FastAPI (sem subir servidor)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def criado(client, produto_valido):
    """Um produto já cadastrado, para os testes de busca, atualização e exclusão."""
    return client.post("/produtos", json=produto_valido).json()


# ---------- Sucesso ----------

def test_criar_produto_retorna_201(client, produto_valido):
    resposta = client.post("/produtos", json=produto_valido)
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo == {"id": 1, **produto_valido}
    assert resposta.headers["Location"] == "/produtos/1"


def test_listar_sem_produtos_retorna_lista_vazia(client):
    resposta = client.get("/produtos")
    assert resposta.status_code == 200
    assert resposta.json() == []


def test_listar_retorna_todos(client, produto_valido):
    client.post("/produtos", json=produto_valido)
    client.post("/produtos", json={**produto_valido, "nome": "Mouse gamer"})
    resposta = client.get("/produtos")
    assert resposta.status_code == 200
    assert [p["nome"] for p in resposta.json()] == ["Teclado mecânico", "Mouse gamer"]


def test_buscar_por_id_retorna_200(client, criado):
    resposta = client.get(f"/produtos/{criado['id']}")
    assert resposta.status_code == 200
    assert resposta.json() == criado


def test_atualizar_retorna_200_com_dados_novos(client, criado):
    novos = {"nome": "Teclado sem fio", "preco": 250.0, "estoque": 3}
    resposta = client.put(f"/produtos/{criado['id']}", json=novos)
    assert resposta.status_code == 200
    assert resposta.json() == {"id": criado["id"], **novos}
    assert client.get(f"/produtos/{criado['id']}").json()["nome"] == "Teclado sem fio"


def test_excluir_retorna_204_e_produto_some(client, criado):
    resposta = client.delete(f"/produtos/{criado['id']}")
    assert resposta.status_code == 204
    assert resposta.content == b""
    assert client.get(f"/produtos/{criado['id']}").status_code == 404


# ---------- Falha: produto inexistente ----------

def test_buscar_inexistente_retorna_404(client):
    resposta = client.get("/produtos/999")
    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Produto não encontrado"}


def test_atualizar_inexistente_retorna_404(client, produto_valido):
    resposta = client.put("/produtos/999", json=produto_valido)
    assert resposta.status_code == 404


def test_excluir_inexistente_retorna_404(client):
    assert client.delete("/produtos/999").status_code == 404


def test_excluir_duas_vezes_retorna_404_na_segunda(client, criado):
    assert client.delete(f"/produtos/{criado['id']}").status_code == 204
    assert client.delete(f"/produtos/{criado['id']}").status_code == 404


# ---------- Validação de dados ----------

@pytest.mark.parametrize(
    "alteracao",
    [
        {"nome": ""},
        {"nome": "ab"},
        {"nome": "x" * 101},
        {"preco": 0},
        {"preco": -5},
        {"estoque": -1},
        {"estoque": 2.5},
    ],
)
def test_criar_com_dado_invalido_retorna_422(client, produto_valido, alteracao):
    resposta = client.post("/produtos", json={**produto_valido, **alteracao})
    assert resposta.status_code == 422
    assert client.get("/produtos").json() == []


def test_criar_sem_campo_obrigatorio_retorna_422(client):
    resposta = client.post("/produtos", json={"nome": "Monitor"})
    assert resposta.status_code == 422


def test_criar_com_corpo_vazio_retorna_422(client):
    assert client.post("/produtos").status_code == 422


def test_atualizar_com_dado_invalido_retorna_422(client, criado):
    invalido = {"nome": criado["nome"], "preco": -1, "estoque": criado["estoque"]}
    resposta = client.put(f"/produtos/{criado['id']}", json=invalido)
    assert resposta.status_code == 422
    assert client.get(f"/produtos/{criado['id']}").json()["preco"] == criado["preco"]


def test_id_que_nao_e_numero_retorna_422(client):
    assert client.get("/produtos/abc").status_code == 422
