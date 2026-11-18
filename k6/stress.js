// Stress Test: carga bem acima da média para achar o limite da API e ver como
// ela degrada. Sobe em degraus: 200, 400 e 600 usuários (4, 8 e 12 vezes os
// 50 usuários do Average Load), mantendo cada nível por um tempo (11 min).
// Uma primeira versão, só até 200 usuários, não mostrou degradação nenhuma
// (resultados/stress-200usuarios.*), por isso os degraus maiores.
// Os limites são mais folgados: se o Stress reprovar, isso é resultado, não erro.

import { fluxoCrud } from './fluxo.js';

export const options = {
  stages: [
    { duration: '2m', target: 200 },
    { duration: '1m', target: 200 },
    { duration: '2m', target: 400 },
    { duration: '1m', target: 400 },
    { duration: '2m', target: 600 },
    { duration: '2m', target: 600 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.05'], // menos de 5% de falhas
    http_req_duration: ['p(95)<1000'], // p95 abaixo de 1 s
    checks: ['rate>0.95'],
  },
};

export default function () {
  fluxoCrud();
}
