"""Testes unitários das regras de validação (sem HTTP)."""

import pytest
from pydantic import ValidationError

from app.schemas import ProdutoEntrada


def test_aceita_produto_valido(produto_valido):
    produto = ProdutoEntrada(**produto_valido)
    assert produto.nome == "Teclado mecânico"
    assert produto.preco == 199.9
    assert produto.estoque == 10


def test_remove_espacos_das_pontas_do_nome():
    produto = ProdutoEntrada(nome="  Mouse  ", preco=50, estoque=0)
    assert produto.nome == "Mouse"


def test_aceita_estoque_zero():
    assert ProdutoEntrada(nome="Cabo", preco=9.9, estoque=0).estoque == 0


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("nome", ""),
        ("nome", "   "),
        ("nome", "ab"),
        ("nome", "x" * 101),
        ("preco", 0),
        ("preco", -10),
        ("estoque", -1),
        ("estoque", 2.5),
        ("estoque", "muitos"),
    ],
)
def test_recusa_valor_invalido(produto_valido, campo, valor):
    dados = {**produto_valido, campo: valor}
    with pytest.raises(ValidationError):
        ProdutoEntrada(**dados)


@pytest.mark.parametrize("campo", ["nome", "preco", "estoque"])
def test_recusa_campo_obrigatorio_faltando(produto_valido, campo):
    dados = {k: v for k, v in produto_valido.items() if k != campo}
    with pytest.raises(ValidationError):
        ProdutoEntrada(**dados)


def test_recusa_campo_que_nao_existe(produto_valido):
    with pytest.raises(ValidationError):
        ProdutoEntrada(**produto_valido, cor="azul")
