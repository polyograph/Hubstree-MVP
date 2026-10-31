"""Testa o servidor de contêiner (servidor.py): estático, segurança e API."""

import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from servidor import criar_servidor  # noqa: E402

TEXTO = json.loads((RAIZ / "tests" / "textos.json").read_text("utf-8"))[2]


@pytest.fixture(scope="module")
def base():
    srv = criar_servidor("127.0.0.1", 0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def pegar(url, dados=None):
    req = urllib.request.Request(url, data=dados, headers={"Content-Type": "application/json"},
                                 method="POST" if dados else "GET")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def test_pagina_inicial_com_cabecalhos_de_seguranca(base):
    status, cab, corpo = pegar(base + "/")
    assert status == 200 and b"Hubstree" in corpo
    assert "frame-ancestors 'none'" in cab["Content-Security-Policy"]
    assert cab["X-Content-Type-Options"] == "nosniff"


def test_sem_listagem_de_pasta(base):
    assert pegar(base + "/js/")[0] == 404


def test_saude(base):
    status, _, corpo = pegar(base + "/saude")
    assert status == 200 and json.loads(corpo)["status"] == "ok"


def test_api_verificar(base):
    status, _, corpo = pegar(base + "/api/verificar", json.dumps({"texto": TEXTO}).encode())
    assert status == 200 and json.loads(corpo)["veredito"] == "PROCESSADO"


def test_post_fora_da_api(base):
    assert pegar(base + "/qualquer", b"{}")[0] == 404
