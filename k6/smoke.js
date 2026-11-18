// Smoke Test: carga mínima e curta, só para provar que o script funciona e
// ver o comportamento inicial da API.
// 2 usuários virtuais por 1 minuto (1 minuto, e não 30 s, porque o relatório
// HTML do k6 só desenha gráficos em testes com mais de 3 vezes o período de
// atualização, que é de 10 s).

import { fluxoCrud } from './fluxo.js';

export const options = {
  vus: 2,
  duration: '1m',
  thresholds: {
    http_req_failed: ['rate<0.01'], // menos de 1% de falhas
    http_req_duration: ['p(95)<300'], // p95 abaixo de 300 ms
    checks: ['rate>0.99'], // mais de 99% dos checks aprovados
  },
};

export default function () {
  fluxoCrud();
}
