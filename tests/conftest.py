import pytest

from app.repository import repositorio


@pytest.fixture(autouse=True)
def limpar_repositorio():
    """Começa e termina cada teste com o armazenamento vazio."""
    repositorio.limpar()
    yield
    repositorio.limpar()


@pytest.fixture
def produto_valido():
    return {"nome": "Teclado mecânico", "preco": 199.9, "estoque": 10}
