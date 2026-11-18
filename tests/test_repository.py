"""Testes unitários do armazenamento em memória (sem HTTP)."""

import pytest

from app.repository import ProdutoRepository
from app.schemas import ProdutoEntrada


@pytest.fixture
def repo():
    return ProdutoRepository()


@pytest.fixture
def entrada(produto_valido):
    return ProdutoEntrada(**produto_valido)


def test_criar_gera_ids_sequenciais(repo, entrada):
    primeiro = repo.criar(entrada)
    segundo = repo.criar(entrada)
    assert (primeiro.id, segundo.id) == (1, 2)
    assert primeiro.nome == entrada.nome


def test_listar_comeca_vazio(repo):
    assert repo.listar() == []


def test_listar_devolve_todos(repo, entrada):
    repo.criar(entrada)
    repo.criar(entrada)
    assert len(repo.listar()) == 2


def test_buscar_existente(repo, entrada):
    criado = repo.criar(entrada)
    assert repo.buscar(criado.id) == criado


def test_buscar_inexistente_devolve_none(repo):
    assert repo.buscar(999) is None


def test_atualizar_existente(repo, entrada):
    criado = repo.criar(entrada)
    novos = ProdutoEntrada(nome="Teclado sem fio", preco=250.0, estoque=3)
    atualizado = repo.atualizar(criado.id, novos)
    assert atualizado.id == criado.id
    assert repo.buscar(criado.id).nome == "Teclado sem fio"


def test_atualizar_inexistente_devolve_none(repo, entrada):
    assert repo.atualizar(999, entrada) is None
    assert repo.listar() == []


def test_excluir_existente(repo, entrada):
    criado = repo.criar(entrada)
    assert repo.excluir(criado.id) is True
    assert repo.buscar(criado.id) is None


def test_excluir_inexistente_devolve_false(repo):
    assert repo.excluir(999) is False


def test_limpar_apaga_tudo_e_reinicia_ids(repo, entrada):
    repo.criar(entrada)
    repo.limpar()
    assert repo.listar() == []
    assert repo.criar(entrada).id == 1
