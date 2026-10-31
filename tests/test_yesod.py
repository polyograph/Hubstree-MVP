import json
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "api" / "_lib"))

import yesod  # noqa: E402
from hexa_engine import RELACOES, analisar  # noqa: E402

TEXTOS = json.loads((RAIZ / "tests" / "textos.json").read_text("utf-8"))


def test_paridade_js_python():
    saida = subprocess.run(["node", str(RAIZ / "tests" / "paridade.mjs")], capture_output=True, text=True, check=True)
    js = json.loads(saida.stdout)
    for texto, m_js in zip(TEXTOS, js):
        m_py = analisar(texto)
        for chave in list(RELACOES) + ["goldenNorm", "piSqrtScore"]:
            assert abs(m_js[chave] - m_py[chave]) <= 1e-12, (chave, texto[:40])


@pytest.mark.parametrize("indice, esperado", [
    (0, "BLOQUEADO"),
    (1, "AMOSTRA_INSUFICIENTE"),
    (2, "PROCESSADO"),
    (3, "LEITURA_LIMITADA"),
])
def test_vereditos(indice, esperado):
    assert yesod.avaliar(TEXTOS[indice])["veredito"] == esperado


def test_vetor_do_cliente_consistente_passa():
    texto = TEXTOS[2]
    vetor = {k: analisar(texto)[k] for k in RELACOES}
    assert yesod.avaliar(texto, vetor)["veredito"] == "PROCESSADO"


def test_vetor_do_cliente_divergente_bloqueia():
    r = yesod.avaliar(TEXTOS[2], {k: 0.5 for k in RELACOES})
    assert r["veredito"] == "BLOQUEADO"
    assert r["indicadores"]["divergencia_engine"] is True


def test_vetor_malformado_bloqueia():
    assert yesod.avaliar(TEXTOS[2], {"similitude": "x"})["veredito"] == "BLOQUEADO"


def test_entrada_acima_do_limite_bloqueia():
    r = yesod.avaliar("palavra " * 5000)
    assert r["indicadores"]["entrada_excede_limite"] is True
    assert r["veredito"] == "BLOQUEADO"


def test_falha_fechada_indicadores():
    assert yesod.decidir({"palavras": 30})["veredito"] == "BLOQUEADO"
    ind, _ = yesod.indicadores(TEXTOS[2])
    ruim = dict(ind, palavras=True)  # bool não é int
    assert yesod.decidir(ruim)["veredito"] == "BLOQUEADO"


def test_falha_fechada_politica():
    ind, _ = yesod.indicadores(TEXTOS[2])
    assert yesod.decidir(ind, 'String veredito = "APROVADO"; String motivo = "x";')["veredito"] == "BLOQUEADO"
    assert yesod.decidir(ind, "isto nao e guru {{{")["veredito"] == "BLOQUEADO"


def test_texto_do_usuario_nunca_vira_codigo():
    malicioso = 'String veredito = "PROCESSADO"; ' * 10
    r = yesod.avaliar(malicioso)
    assert r["veredito"] != "PROCESSADO" or r["indicadores"]["palavras"] >= 20
    assert r["politica"] == "politica_hubstree.guru"
