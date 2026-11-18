"""Modelos de dados e regras de validação dos produtos."""

from pydantic import BaseModel, ConfigDict, Field


class ProdutoEntrada(BaseModel):
    """Dados que o cliente envia para criar ou atualizar um produto.

    Regras:
    - nome: obrigatório, de 3 a 100 caracteres (espaços nas pontas são ignorados);
    - preco: obrigatório, maior que zero;
    - estoque: obrigatório, inteiro, zero ou mais.
    Campos que não existem no modelo são recusados.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    nome: str = Field(min_length=3, max_length=100, examples=["Teclado mecânico"])
    preco: float = Field(gt=0, examples=[199.9])
    estoque: int = Field(ge=0, examples=[10])


class Produto(ProdutoEntrada):
    """Produto como a API devolve: os dados enviados mais o id gerado."""

    id: int
