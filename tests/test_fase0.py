"""Fase 0: fronteira de entrada canônica (NFC, pontos de código, hash, Unicode válido).

Os casos seguem a especificação técnica revisada pela Luna em 31/10/2026.
"""

import hashlib
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "api"))
sys.path.insert(0, str(RAIZ / "api" / "_lib"))

import yesod  # noqa: E402
from hexa_engine import RELACOES, analisar  # noqa: E402
from test_endpoint import post, url  # noqa: E402,F401  (fixture do servidor local)
from verificar import MAX_CORPO  # noqa: E402

TEXTO = json.loads((RAIZ / "tests" / "textos.json").read_text("utf-8"))[2]


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def vetor_de(t):
    m = analisar(unicodedata.normalize("NFC", t)[:yesod.LIMITE_CARACTERES])
    return {k: m[k] for k in RELACOES}


# ── servidor ─────────────────────────────────────────────────────────────

def test_nfd_nao_estoura_limite_que_o_nfc_respeita():
    nfd = unicodedata.normalize("NFD", "ação é " * 3000)[:20010]
    assert len(nfd) == 20010 and len(unicodedata.normalize("NFC", nfd)) == 14007
    r = yesod.avaliar(nfd)
    assert r["indicadores"]["entrada_excede_limite"] is False
    assert r["codigo"] != "ENTRADA_ACIMA_LIMITE"


def test_limite_em_pontos_de_codigo():
    exato = "a" * 19000 + "😀" * 1000  # 20.000 pontos de código, 21.000 unidades UTF-16
    assert yesod.indicadores(exato)[0]["entrada_excede_limite"] is False
    assert yesod.indicadores(exato + "a")[0]["entrada_excede_limite"] is True


@pytest.mark.parametrize("estado,hash_cliente", [
    ("verificado", sha(unicodedata.normalize("NFC", TEXTO))),
    ("ausente_legado", None),
    ("divergente", sha("outro texto")),
])
def test_hash_status(estado, hash_cliente):
    r = yesod.avaliar(TEXTO, vetor_de(TEXTO), hash_cliente)
    assert r["proveniencia"]["hash_status"] == estado
    assert r["indicadores"]["hash_divergente"] is (estado == "divergente")
    if estado == "divergente":
        assert (r["veredito"], r["codigo"]) == ("BLOQUEADO", "HASH_DIVERGENTE")
    else:
        assert r["veredito"] == "PROCESSADO"


def test_hash_cobre_texto_nfc_integral_e_trecho_analisado():
    longo = unicodedata.normalize("NFD", TEXTO) + " palavra" * 3000
    nfc = unicodedata.normalize("NFC", longo)
    p = yesod.avaliar(longo)["proveniencia"]
    assert p["input_sha256"] == sha(nfc)
    assert p["analise_sha256"] == sha(nfc[:yesod.LIMITE_CARACTERES])


def test_resposta_de_sucesso_declara_origem_e_codigo():
    r = yesod.avaliar(TEXTO, vetor_de(TEXTO), sha(unicodedata.normalize("NFC", TEXTO)))
    assert r["origem_resultado"] == "servidor"
    assert r["politica_avaliada"] is True and r["politica_ok"] is True
    assert r["codigo"] == "PROCESSADO"
    assert set(r["proveniencia"]) == {"input_sha256", "analise_sha256", "hash_status"}


def test_falha_antes_da_politica_nao_conta_como_avaliada():
    r = yesod.decidir({"palavras": 30})
    assert r["politica_avaliada"] is False and r["codigo"] == "INDICADORES_INVALIDOS"


def test_cliente_legado_com_recorte_utf16_bloqueia_por_divergencia():
    # 18.000 ASCII + 1.000 emojis separados por espaço = 20.000 pontos de código, 21.000 unidades UTF-16.
    texto = ("palavra " * 2250) + ("😀 " * 1000)
    assert len(texto) == 20000
    utf16 = texto.encode("utf-16-le")[: yesod.LIMITE_CARACTERES * 2].decode("utf-16-le")  # String.slice() do cliente 2.0
    r = yesod.avaliar(texto, vetor_de(utf16))
    assert (r["veredito"], r["codigo"]) == ("BLOQUEADO", "DIVERGENCIA_ENGINE")


# ── paridade navegador × servidor ────────────────────────────────────────

CASOS_FRONTEIRA = {
    "nfd": unicodedata.normalize("NFD", "ação é " * 3000)[:20010],
    **{f"emoji_{p}": "a" * (p - 1) + "😀" + "b" * 50 for p in (19999, 20000, 20001)},
    "exato_20000_pontos": "a" * 19000 + "😀" * 1000,
}

SCRIPT_NODE = """
import { executar } from './public/js/pipeline.js';
const casos = JSON.parse(await new Promise((ok) => { let d = ''; process.stdin.on('data', (c) => d += c); process.stdin.on('end', () => ok(d)); }));
globalThis.fetch = async (_url, init) => { globalThis.ultimo = JSON.parse(init.body); return new Response('{}', { status: 200 }); };
const saida = {};
for (const [nome, texto] of Object.entries(casos)) {
  const r = await executar(texto);
  saida[nome] = { caracteres: r.keter.caracteres, excede: r.keter.excedeLimite, analise: r.keter.hash,
                  entrada: r.keter.inputSha256, enviado: globalThis.ultimo.input_sha256 };
}
process.stdout.write(JSON.stringify(saida));
"""


def test_limite_recorte_e_hash_iguais_no_navegador_e_no_servidor():
    proc = subprocess.run(["node", "--input-type=module", "-e", SCRIPT_NODE], cwd=RAIZ,
                          input=json.dumps(CASOS_FRONTEIRA), capture_output=True, text=True, check=True)
    js = json.loads(proc.stdout)
    for nome, texto in CASOS_FRONTEIRA.items():
        nfc, analise = yesod.canonico(texto)
        ind, _ = yesod.indicadores(texto)
        assert js[nome]["caracteres"] == len(nfc), nome
        assert js[nome]["excede"] is ind["entrada_excede_limite"], nome
        assert js[nome]["analise"] == sha(analise), nome
        assert js[nome]["entrada"] == js[nome]["enviado"] == sha(nfc), nome
        # o servidor confere o hash enviado e o aceita
        assert yesod.proveniencia(texto, js[nome]["enviado"])["hash_status"] == "verificado", nome


# ── endpoint HTTP ────────────────────────────────────────────────────────

@pytest.mark.parametrize("bruto,codigo", [
    (b'{"texto": "a\\ud800b"}', "TEXTO_UNICODE_INVALIDO"),
    (b'{"texto": "a\\u0000b"}', "TEXTO_CONTROLE_INVALIDO"),
    (b'{"texto": "a\\u001fb"}', "TEXTO_CONTROLE_INVALIDO"),
    (b'{"texto": "a", "input_sha256": "abc"}', "HASH_MALFORMADO"),
    (b'{"texto": "a", "input_sha256": "' + b"A" * 64 + b'"}', "HASH_MALFORMADO"),
    (b'{"texto": "a", "input_sha256": 5}', "HASH_MALFORMADO"),
    (b'{"texto": "a", "outra": 1}', "CHAVE_NAO_PERMITIDA"),
])
def test_recusas_400_com_codigo(url, bruto, codigo):  # noqa: F811
    status, corpo = post(url, bruto)
    assert status == 400 and corpo["codigo"] == codigo


def test_tab_e_quebras_de_linha_sao_aceitas(url):  # noqa: F811
    texto = TEXTO.replace(" ", "\t", 3) + "\r\n\r\nOutro paragrafo com varias palavras para manter a amostra suficiente."
    status, corpo = post(url, json.dumps({"texto": texto}).encode())
    assert status == 200 and corpo["origem_resultado"] == "servidor"


def test_corpo_acima_do_limite_vira_413_com_codigo(url):  # noqa: F811
    status, corpo = post(url, json.dumps({"texto": "x" * (MAX_CORPO + 10)}).encode())
    assert status == 413 and corpo["codigo"] == "CORPO_REQUISICAO_ACIMA_LIMITE"


def test_maior_corpo_valido_cabe_em_max_corpo(url):  # noqa: F811
    # 20.000 pontos de código: emojis de 4 bytes intercalados com aspas e barras (2 bytes escapadas)
    texto = ("😀" * 18 + '"' + "\\") * 1000
    assert len(texto) == 20000
    corpo = json.dumps({"texto": texto, "vetor": vetor_de(texto), "input_sha256": sha(texto)}, ensure_ascii=False).encode()
    assert len(corpo) <= MAX_CORPO
    status, resposta = post(url, corpo)
    assert status == 200 and resposta["proveniencia"]["hash_status"] == "verificado"
