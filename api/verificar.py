"""Função serverless da Vercel: POST /api/verificar (etapa Yesod).

Corpo: {"texto": "...", "vetor": {"similitude": 0.4, ...}, "input_sha256": "..."}
Resposta: veredito da política GuruDev, indicadores, métricas recalculadas e proveniência.
Erros de contrato devolvem HTTP 400/413 com um "codigo" estável.
"""

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "_lib"))

from yesod import HASH_HEX, LIMITE_CARACTERES, avaliar, codigo_texto_invalido  # noqa: E402

# Pior caso válido: 4 bytes UTF-8 por ponto de código. Controles C0 (que viram \\u00XX,
# 6 bytes) são recusados, e aspas, barra e tab/LF/CR ocupam 2 bytes escapados.
MAX_CORPO = LIMITE_CARACTERES * 4 + 4096
CHAVES_PERMITIDAS = {"texto", "vetor", "input_sha256"}


class CorpoInvalido(ValueError):
    def __init__(self, mensagem, codigo="CORPO_INVALIDO"):
        super().__init__(mensagem)
        self.codigo = codigo


def _sem_duplicatas(pares):
    chaves = [k for k, _ in pares]
    if len(chaves) != len(set(chaves)):
        raise CorpoInvalido("chave duplicada", "CHAVE_DUPLICADA")
    return dict(pares)


def _recusar_constante(nome):
    raise CorpoInvalido(f"constante não permitida: {nome}", "CONSTANTE_NAO_PERMITIDA")


def ler_corpo(bruto):
    """Contrato do corpo: objeto JSON com "texto" (string), "vetor" (objeto, opcional) e
    "input_sha256" (64 hex minúsculos, opcional). Recusa chaves duplicadas, chaves extras,
    NaN/Infinity, surrogates isolados e controles C0. O conteúdo de "vetor" é validado
    depois, no yesod, e um vetor fora do contrato bloqueia pela política."""
    corpo = json.loads(bruto.decode("utf-8"), object_pairs_hook=_sem_duplicatas,
                       parse_constant=_recusar_constante)
    if not isinstance(corpo, dict) or "texto" not in corpo:
        raise CorpoInvalido("esperado {texto: string, vetor?: objeto, input_sha256?: string}")
    if not set(corpo) <= CHAVES_PERMITIDAS:
        raise CorpoInvalido("chave fora do contrato", "CHAVE_NAO_PERMITIDA")
    if not isinstance(corpo["texto"], str):
        raise CorpoInvalido("texto deve ser string")
    invalido = codigo_texto_invalido(corpo["texto"])
    if invalido:
        raise CorpoInvalido("texto com caractere não permitido", invalido)
    vetor = corpo.get("vetor")
    if vetor is not None and not isinstance(vetor, dict):
        raise CorpoInvalido("vetor deve ser objeto")
    hash_cliente = corpo.get("input_sha256")
    if hash_cliente is not None and not (isinstance(hash_cliente, str) and HASH_HEX.fullmatch(hash_cliente)):
        raise CorpoInvalido("input_sha256 deve ter 64 caracteres hexadecimais minúsculos", "HASH_MALFORMADO")
    return corpo["texto"], vetor, hash_cliente


class handler(BaseHTTPRequestHandler):
    def _responder(self, status, corpo):
        dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_GET(self):
        self._responder(200, {"servico": "Hubstree · Yesod", "uso": "POST {texto, vetor?, input_sha256?}"})

    def do_POST(self):
        try:
            tamanho = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            tamanho = 0
        if tamanho > MAX_CORPO:
            self._responder(413, {"erro": "corpo grande demais", "codigo": "CORPO_REQUISICAO_ACIMA_LIMITE"})
            return
        if tamanho <= 0:
            self._responder(400, {"erro": "corpo ausente", "codigo": "CORPO_AUSENTE"})
            return
        try:
            texto, vetor, hash_cliente = ler_corpo(self.rfile.read(tamanho))
        except CorpoInvalido as e:
            self._responder(400, {"erro": f"corpo inválido: {e}", "codigo": e.codigo})
            return
        except (ValueError, UnicodeDecodeError, RecursionError) as e:  # JSONDecodeError herda de ValueError
            self._responder(400, {"erro": f"corpo inválido: {type(e).__name__}", "codigo": "CORPO_INVALIDO"})
            return
        try:
            resultado = avaliar(texto, vetor, hash_cliente)
        except Exception as e:  # falha fechada também no transporte: nunca um 500 sem veredito
            resultado = {"veredito": "BLOQUEADO", "motivo": f"erro interno: {type(e).__name__}",
                         "codigo": "ERRO_INTERNO", "politica_ok": False, "politica_avaliada": False,
                         "origem_resultado": "servidor"}
        self._responder(200, resultado)
