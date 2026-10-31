"""Testa o endpoint HTTP real (api/verificar.py) num servidor local com threads."""

import json
import sys
import threading
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "api"))
sys.path.insert(0, str(RAIZ / "api" / "_lib"))

from hexa_engine import RELACOES, analisar  # noqa: E402
from verificar import handler  # noqa: E402

TEXTO = json.loads((RAIZ / "tests" / "textos.json").read_text("utf-8"))[2]


class Servidor(ThreadingHTTPServer):
    request_queue_size = 128  # a fila padrão (5) recusava rajadas do teste de concorrência
    daemon_threads = True


@pytest.fixture(scope="module")
def url():
    servidor = Servidor(("127.0.0.1", 0), handler)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{servidor.server_address[1]}/api/verificar"
    servidor.shutdown()


def post(url, corpo_bytes):
    req = urllib.request.Request(url, data=corpo_bytes, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_caminho_feliz(url):
    vetor = {k: analisar(TEXTO)[k] for k in RELACOES}
    status, corpo = post(url, json.dumps({"texto": TEXTO, "vetor": vetor}).encode())
    assert status == 200 and corpo["veredito"] == "PROCESSADO"


@pytest.mark.parametrize("bruto", [
    b"isto nao e json",
    b"[]",
    b'"texto"',
    b'{"texto": 5}',
    b'{"vetor": {}}',
    b'{"texto": "a", "vetor": [1, 2]}',
    b'{"texto": "a", "outra": 1}',
    b'{"texto": "a", "texto": "b"}',
    b'{"texto": "a", "vetor": {"similitude": NaN}}',
    b'{"texto": "a", "vetor": {"similitude": Infinity}}',
    b"\xff\xfe\x00",
    b"[" * 3000 + b"]" * 3000,  # aninhamento profundo (RecursionError)
])
def test_corpos_invalidos_viram_400(url, bruto):
    status, corpo = post(url, bruto)
    assert status == 400 and "erro" in corpo


def test_vetor_com_strings_bloqueia_pela_politica(url):
    status, corpo = post(url, json.dumps({"texto": TEXTO, "vetor": {k: "0.5" for k in RELACOES}}).encode())
    assert status == 200 and corpo["veredito"] == "BLOQUEADO"
    assert corpo["indicadores"]["vetor_cliente_invalido"] is True


def test_requisicoes_concorrentes(url):
    vetor = {k: analisar(TEXTO)[k] for k in RELACOES}
    corpo = json.dumps({"texto": TEXTO, "vetor": vetor}).encode()
    with ThreadPoolExecutor(max_workers=16) as pool:
        resultados = list(pool.map(lambda _: post(url, corpo), range(64)))
    assert all(s == 200 and c["veredito"] == "PROCESSADO" for s, c in resultados)
