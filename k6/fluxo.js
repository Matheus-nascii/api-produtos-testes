// Fluxo usado pelos três testes de carga: cada usuário virtual cria um
// produto, lista todos, busca o criado, atualiza e exclui. Toda resposta tem
// um check do código esperado. As tags "name" agrupam as URLs com id no
// relatório (senão cada /produtos/123 apareceria como uma URL diferente).

import http from 'k6/http';
import { check, sleep } from 'k6';

// 127.0.0.1 em vez de localhost: no Windows, "localhost" tenta primeiro o
// endereço IPv6 (::1), onde a API não está ouvindo.
export const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000';

const JSON_HEADERS = { 'Content-Type': 'application/json' };

export function fluxoCrud() {
  const novo = JSON.stringify({ nome: `Produto VU ${__VU}`, preco: 19.9, estoque: 10 });
  const criado = http.post(`${BASE_URL}/produtos`, novo, {
    headers: JSON_HEADERS,
    tags: { name: 'POST /produtos' },
  });
  const criou = check(criado, { 'POST /produtos retorna 201': (r) => r.status === 201 });
  if (!criou) {
    sleep(1);
    return;
  }
  const id = criado.json('id');

  const lista = http.get(`${BASE_URL}/produtos`, { tags: { name: 'GET /produtos' } });
  check(lista, { 'GET /produtos retorna 200': (r) => r.status === 200 });

  const busca = http.get(`${BASE_URL}/produtos/${id}`, { tags: { name: 'GET /produtos/{id}' } });
  check(busca, { 'GET /produtos/{id} retorna 200': (r) => r.status === 200 });

  const alterado = JSON.stringify({ nome: `Produto VU ${__VU} alterado`, preco: 25.0, estoque: 5 });
  const atualizacao = http.put(`${BASE_URL}/produtos/${id}`, alterado, {
    headers: JSON_HEADERS,
    tags: { name: 'PUT /produtos/{id}' },
  });
  check(atualizacao, { 'PUT /produtos/{id} retorna 200': (r) => r.status === 200 });

  const exclusao = http.del(`${BASE_URL}/produtos/${id}`, null, {
    tags: { name: 'DELETE /produtos/{id}' },
  });
  check(exclusao, { 'DELETE /produtos/{id} retorna 204': (r) => r.status === 204 });

  // Pausa de 1 s, como uma pessoa real entre uma ação e outra.
  sleep(1);
}
