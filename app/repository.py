"""Armazenamento dos produtos em memória."""

from __future__ import annotations

from app.schemas import Produto, ProdutoEntrada


class ProdutoRepository:
    """Guarda os produtos num dicionário, indexado pelo id.

    Os dados ficam só na memória do processo: somem quando a API é reiniciada
    e não são compartilhados entre processos. Por isso a API roda com um único
    processo do Uvicorn.
    """

    def __init__(self) -> None:
        self._produtos: dict[int, Produto] = {}
        self._proximo_id = 1

    def criar(self, dados: ProdutoEntrada) -> Produto:
        produto = Produto(id=self._proximo_id, **dados.model_dump())
        self._produtos[produto.id] = produto
        self._proximo_id += 1
        return produto

    def listar(self) -> list[Produto]:
        return list(self._produtos.values())

    def buscar(self, produto_id: int) -> Produto | None:
        return self._produtos.get(produto_id)

    def atualizar(self, produto_id: int, dados: ProdutoEntrada) -> Produto | None:
        if produto_id not in self._produtos:
            return None
        produto = Produto(id=produto_id, **dados.model_dump())
        self._produtos[produto_id] = produto
        return produto

    def excluir(self, produto_id: int) -> bool:
        return self._produtos.pop(produto_id, None) is not None

    def limpar(self) -> None:
        """Apaga tudo e volta o id para 1 (usado entre os testes)."""
        self._produtos.clear()
        self._proximo_id = 1


repositorio = ProdutoRepository()
