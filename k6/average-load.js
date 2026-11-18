// Average Load Test: uso normal. Cenário hipotético de uma loja pequena com
// cerca de 50 pessoas usando o sistema ao mesmo tempo no horário de pico.
// Sobe até 50 usuários em 2 min, mantém 5 min e desce em 1 min (8 min).

import { fluxoCrud } from './fluxo.js';

export const options = {
  stages: [
    { duration: '2m', target: 50 },
    { duration: '5m', target: 50 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'], // menos de 1% de falhas
    http_req_duration: ['p(95)<500'], // p95 abaixo de 500 ms
    checks: ['rate>0.99'],
  },
};

export default function () {
  fluxoCrud();
}
