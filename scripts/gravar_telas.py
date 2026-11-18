"""Grava as telas do CRUD no Swagger, para o vídeo da apresentação.

Liga a API (memória limpa), abre o Swagger num navegador controlado pelo
Playwright e executa, nesta ordem: POST, GET (lista), GET por id, PUT, DELETE,
GET do produto excluído (404) e POST com preço negativo (422).
Para cada passo salva um print do pedido e da resposta em resultados/telas/
e o resumo em passos.json.
"""

import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[1]
TELAS = RAIZ / 'resultados' / 'telas'
API = 'http://127.0.0.1:8000'
DOCS = 'http://localhost:8000/docs'
LARGURA, ALTURA = 1440, 648
PAUSA = 1.2  # segundos entre ações, para o vídeo ficar acompanhável


def api_respondendo():
    try:
        urllib.request.urlopen(API + '/produtos', timeout=2)
        return True
    except Exception:
        return False


def foto(pagina, nome):
    caminho = TELAS / f'{nome}.png'
    pagina.screenshot(path=str(caminho))
    print('  print:', caminho.name)


def topo(pagina, elemento, folga=8):
    pagina.evaluate('([el, f]) => window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - f)',
                    [elemento.element_handle(), folga])
    time.sleep(0.3)


def abrir(pagina, operacao):
    op = pagina.locator(f'#operations-produtos-{operacao}')
    if 'is-open' not in (op.get_attribute('class') or ''):
        op.locator('.opblock-summary-control').click()
    botao = op.locator('.try-out__btn')
    botao.wait_for()
    if botao.inner_text().strip() == 'Try it out':
        botao.click()
    op.locator('button.execute').wait_for()
    time.sleep(PAUSA)
    return op


def executar(pagina, op, nome, corpo=None, produto_id=None):
    if produto_id is not None:
        campo = op.locator('input[placeholder="produto_id"]')
        campo.fill(str(produto_id))
    if corpo is not None:
        op.locator('textarea.body-param__text').fill(json.dumps(corpo, ensure_ascii=False, indent=2))
    topo(pagina, op)
    foto(pagina, f'{nome}-pedido')
    time.sleep(PAUSA)
    op.locator('button.execute').click()
    status = op.locator('.live-responses-table .response .response-col_status').first
    status.wait_for()
    time.sleep(PAUSA)
    codigo = status.inner_text().strip()
    corpo_resposta = ''
    blocos = op.locator('.live-responses-table .response .microlight')
    if blocos.count():
        corpo_resposta = blocos.first.inner_text()
    topo(pagina, op.locator('.responses-wrapper').first, folga=4)
    foto(pagina, f'{nome}-resposta')
    time.sleep(PAUSA)
    print(f'{nome}: {codigo}')
    return {'passo': nome, 'codigo': codigo, 'resposta': corpo_resposta}


def main():
    TELAS.mkdir(parents=True, exist_ok=True)
    if api_respondendo():
        print('Já tem uma API ligada na porta 8000. Feche a janela do 3-iniciar-api.bat e rode de novo.')
        sys.exit(1)
    api = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'],
                           cwd=RAIZ)
    passos = []
    try:
        for _ in range(60):
            if api_respondendo():
                break
            time.sleep(0.5)
        else:
            print('A API não respondeu.')
            sys.exit(1)

        with sync_playwright() as p:
            try:
                navegador = p.chromium.launch(channel='msedge')
            except Exception:
                navegador = p.chromium.launch()
            contexto = navegador.new_context(
                viewport={'width': LARGURA, 'height': ALTURA}, device_scale_factor=1.5, locale='pt-BR')
            pagina = contexto.new_page()
            pagina.goto(DOCS, wait_until='networkidle')
            pagina.wait_for_selector('.opblock')
            time.sleep(PAUSA)
            foto(pagina, '00-swagger')

            produto = {'nome': 'Teclado mecânico', 'preco': 199.9, 'estoque': 10}
            op = abrir(pagina, 'criar_produto_produtos_post')
            passos.append(executar(pagina, op, '01-post', corpo=produto))
            with urllib.request.urlopen(API + '/produtos', timeout=5) as r:
                produto_id = json.loads(r.read())[-1]['id']

            op = abrir(pagina, 'listar_produtos_produtos_get')
            passos.append(executar(pagina, op, '02-get-lista'))

            op = abrir(pagina, 'buscar_produto_produtos__produto_id__get')
            passos.append(executar(pagina, op, '03-get-id', produto_id=produto_id))

            op = abrir(pagina, 'atualizar_produto_produtos__produto_id__put')
            novo = {'nome': 'Teclado mecânico', 'preco': 179.9, 'estoque': 8}
            passos.append(executar(pagina, op, '04-put', corpo=novo, produto_id=produto_id))

            op = abrir(pagina, 'excluir_produto_produtos__produto_id__delete')
            passos.append(executar(pagina, op, '05-delete', produto_id=produto_id))

            op = abrir(pagina, 'buscar_produto_produtos__produto_id__get')
            passos.append(executar(pagina, op, '06-get-404', produto_id=produto_id))

            op = abrir(pagina, 'criar_produto_produtos_post')
            invalido = {'nome': 'Mouse sem fio', 'preco': -5, 'estoque': 3}
            passos.append(executar(pagina, op, '07-post-422', corpo=invalido))

            contexto.close()
            navegador.close()
    finally:
        api.terminate()
        (TELAS / 'passos.json').write_text(json.dumps(passos, ensure_ascii=False, indent=2), encoding='utf-8')
    print('TELAS_OK')


if __name__ == '__main__':
    main()
