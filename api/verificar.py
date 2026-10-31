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
            corpo = json.loads(self.rfile.read(tamanho).decode("utf-8"))
            texto = corpo.get("texto", "")
            vetor = corpo.get("vetor")
            if not isinstance(texto, str) or (vetor is not None and not isinstance(vetor, dict)):
                raise ValueError
        except (ValueError, UnicodeDecodeError, AttributeError):
            self._responder(400, {"erro": "JSON inválido: esperado {texto: string, vetor?: objeto}"})
            return
        self._responder(200, avaliar(texto, vetor))
