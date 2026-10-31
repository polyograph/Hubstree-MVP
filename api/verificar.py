"""Função serverless da Vercel: POST /api/verificar (etapa Yesod).

Corpo: {"texto": "...", "vetor": {"similitude": 0.4, ...}}
Resposta: veredito da política GuruDev, indicadores e métricas recalculadas.
"""

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "_lib"))

from yesod import LIMITE_CARACTERES, avaliar  # noqa: E402

MAX_CORPO = LIMITE_CARACTERES * 4 + 4096  # UTF-8 pode usar até 4 bytes por caractere
CHAVES_PERMITIDAS = {"texto", "vetor"}


class CorpoInvalido(ValueError):
    pass


def _sem_duplicatas(pares):
    chaves = [k for k, _ in pares]
    if len(chaves) != len(set(chaves)):
        raise CorpoInvalido("chave duplicada")
    return dict(pares)


def _recusar_constante(nome):
    raise CorpoInvalido(f"constante não permitida: {nome}")


def ler_corpo(bruto):
    """Contrato do corpo: objeto JSON só com "texto" (string) e "vetor" (objeto, opcional).
    Recusa chaves duplicadas, chaves extras e NaN/Infinity. O conteúdo de "vetor"
    é validado depois, no yesod, e um vetor fora do contrato bloqueia pela política."""
    corpo = json.loads(bruto.decode("utf-8"), object_pairs_hook=_sem_duplicatas,
                       parse_constant=_recusar_constante)
    if not isinstance(corpo, dict) or not set(corpo) <= CHAVES_PERMITIDAS or "texto" not in corpo:
        raise CorpoInvalido("esperado {texto: string, vetor?: objeto}")
    if not isinstance(corpo["texto"], str):
        raise CorpoInvalido("texto deve ser string")
    vetor = corpo.get("vetor")
    if vetor is not None and not isinstance(vetor, dict):
        raise CorpoInvalido("vetor deve ser objeto")
    return corpo["texto"], vetor


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
        self._responder(200, {"servico": "Hubstree · Yesod", "uso": "POST {texto, vetor}"})

    def do_POST(self):
        try:
            tamanho = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            tamanho = 0
        if tamanho <= 0 or tamanho > MAX_CORPO:
            self._responder(413 if tamanho > MAX_CORPO else 400, {"erro": "corpo ausente ou grande demais"})
            return
        try:
            texto, vetor = ler_corpo(self.rfile.read(tamanho))
        except (ValueError, UnicodeDecodeError, RecursionError) as e:  # CorpoInvalido e JSONDecodeError herdam de ValueError
            self._responder(400, {"erro": f"corpo inválido: {type(e).__name__}"})
            return
        try:
            resultado = avaliar(texto, vetor)
        except Exception as e:  # falha fechada também no transporte: nunca um 500 sem veredito
            resultado = {"veredito": "BLOQUEADO", "motivo": f"erro interno: {type(e).__name__}", "politica_ok": False}
        self._responder(200, resultado)
