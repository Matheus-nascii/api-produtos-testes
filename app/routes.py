"""Endpoints REST do recurso /produtos."""

from typing import List

from fastapi import APIRouter, HTTPException, Response, status

from app.repository import repositorio
from app.schemas import Produto, ProdutoEntrada

router = APIRouter(prefix="/produtos", tags=["produtos"])

NAO_ENCONTRADO = "Produto não encontrado"

# As funções são "async def" de propósito: assim todas rodam na mesma thread
# (o event loop do Uvicorn) e o dicionário em memória nunca é alterado por
# duas requisições ao mesmo tempo.


@router.post(
    "",
    response_model=Produto,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um produto",
)
async def criar_produto(dados: ProdutoEntrada, response: Response) -> Produto:
    produto = repositorio.criar(dados)
    response.headers["Location"] = f"/produtos/{produto.id}"
    return produto


@router.get("", response_model=List[Produto], summary="Lista todos os produtos")
async def listar_produtos() -> List[Produto]:
    return repositorio.listar()


@router.get("/{produto_id}", response_model=Produto, summary="Busca um produto pelo id")
async def buscar_produto(produto_id: int) -> Produto:
    produto = repositorio.buscar(produto_id)
    if produto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NAO_ENCONTRADO)
    return produto


@router.put("/{produto_id}", response_model=Produto, summary="Atualiza um produto")
async def atualizar_produto(produto_id: int, dados: ProdutoEntrada) -> Produto:
    produto = repositorio.atualizar(produto_id, dados)
    if produto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NAO_ENCONTRADO)
    return produto


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui um produto",
)
async def excluir_produto(produto_id: int) -> Response:
    if not repositorio.excluir(produto_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NAO_ENCONTRADO)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
