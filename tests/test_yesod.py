import json
import subprocess
import unicodedata
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "api" / "_lib"))

import yesod  # noqa: E402
from hexa_engine import RELACOES, _normalizar, analisar, contar  # noqa: E402

TEXTOS = json.loads((RAIZ / "tests" / "textos.json").read_text("utf-8"))


def _js(arquivo):
    saida = subprocess.run(["node", str(RAIZ / "tests" / "paridade.mjs"), arquivo],
                           capture_output=True, text=True, check=True, encoding="utf-8")
    return json.loads(saida.stdout)


@pytest.mark.parametrize("arquivo", ["textos.json", "unicode_amostras.json"])
def test_paridade_js_python(arquivo):
    textos = json.loads((RAIZ / "tests" / arquivo).read_text("utf-8"))
    js = _js(arquivo)
    assert len(js) == len(textos)
    comparados = 0
    for texto, r in zip(textos, js):
        # Contrato: a paridade vale para caracteres atribuídos nas duas bases Unicode.
        # Caracteres que o Python ainda não conhece (categoria Cn) podem ter ordem NFD
        # diferente; nesse caso o Yesod detecta a divergência e bloqueia (teste abaixo).
        if any(unicodedata.category(c) == "Cn" for c in texto):
            continue
        comparados += 1
        assert r["n"] == _normalizar(texto), texto[:40]
        assert r["c"] == contar(texto), texto[:40]
        m_py = analisar(texto)
        for chave in list(RELACOES) + ["goldenNorm", "piSqrtScore"]:
            assert abs(r["m"][chave] - m_py[chave]) <= 1e-12, (chave, texto[:40])
    assert comparados >= min(len(textos), 400)


def test_divergencia_de_versao_unicode_e_bloqueada():
    # Simula um navegador com outra base Unicode: o vetor dele não bate com o do servidor.
    textos = json.loads((RAIZ / "tests" / "unicode_amostras.json").read_text("utf-8"))
    js = _js("unicode_amostras.json")
    divergentes = [(t, r) for t, r in zip(textos, js)
                   if any(abs(r["m"][k] - analisar(t)[k]) > 1e-9 for k in RELACOES)]
    for texto, r in divergentes:
        vetor = {k: r["m"][k] for k in RELACOES}
        assert yesod.avaliar(texto, vetor)["veredito"] == "BLOQUEADO"


def test_contrato_de_normalizacao():
    # Remove só U+0300–U+036F após NFD; marcas fora do bloco permanecem nos dois lados.
    assert _normalizar("Ação É") == "acao e"
    assert _normalizar("a\u1ab0") == "a\u1ab0"
    assert _normalizar("c\u20d7") == "c\u20d7"
    assert _normalizar("\uac00") == "\u1100\u1161"  # hangul decomposto em NFD
    assert _normalizar("ÉTICA") == _normalizar("e\u0301tica")


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


@pytest.mark.parametrize("vetor", [
    {k: "0.5" for k in RELACOES},                      # strings conversíveis
    {k: True for k in RELACOES},                       # booleanos
    {k: float("nan") for k in RELACOES},               # NaN
    {k: float("inf") for k in RELACOES},               # infinito
    {k: 1.5 for k in RELACOES},                        # fora de [0,1]
    {k: 0.5 for k in RELACOES[:5]},                    # chave faltando
    {**{k: 0.5 for k in RELACOES}, "extra": 0.1},      # chave extra
    {k: [0.5] for k in RELACOES},                      # lista
    {k: None for k in RELACOES},                       # nulo
])
def test_vetor_fora_do_contrato_bloqueia(vetor):
    r = yesod.avaliar(TEXTOS[2], vetor)
    assert r["indicadores"]["vetor_cliente_invalido"] is True
    assert r["veredito"] == "BLOQUEADO"


def test_vetor_inteiro_valido_e_aceito():
    assert yesod.vetor_cliente_valido({k: 0 for k in RELACOES}) is True
    assert yesod.vetor_cliente_valido({k: 1 for k in RELACOES}) is True


def test_concorrencia_mesmo_resultado_que_sequencial():
    from concurrent.futures import ThreadPoolExecutor
    textos = [TEXTOS[i % 4] + (" extra" * (i % 7)) for i in range(120)]
    esperado = [yesod.avaliar(t)["veredito"] for t in textos]
    with ThreadPoolExecutor(max_workers=24) as pool:
        obtido = list(pool.map(lambda t: yesod.avaliar(t)["veredito"], textos))
    assert obtido == esperado
