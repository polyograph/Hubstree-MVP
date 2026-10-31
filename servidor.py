"""Servidor do Hubstree para contêiner (Cloud Run) e uso local.

Serve o frontend estático de public/ e atende POST /api/verificar com a mesma
função usada na Vercel (api/verificar.py). Só biblioteca padrão do Python.

Uso local:   python3 servidor.py           -> http://127.0.0.1:8000
Contêiner:   PORT e HOST vêm do ambiente   (Cloud Run define PORT)
"""

import os
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PUBLICO = RAIZ / "public"
sys.path.insert(0, str(RAIZ / "api"))

from verificar import handler as Funcao  # noqa: E402

CABECALHOS_SEGURANCA = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; "
        "script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"
    ),
}


class Hubstree(SimpleHTTPRequestHandler):
    server_version = "Hubstree"
    sys_version = ""

    def end_headers(self):
        for nome, valor in CABECALHOS_SEGURANCA.items():
            self.send_header(nome, valor)
        if self.path.split("?")[0].endswith((".js", ".css")):
            self.send_header("Cache-Control", "public, max-age=300")
        super().end_headers()

    def list_directory(self, path):  # sem listagem de pastas
        self.send_error(404)
        return None

    def do_GET(self):
        if self.path.split("?")[0] == "/api/verificar":
            Funcao.do_GET(self)
        elif self.path.split("?")[0] == "/saude":
            Funcao._responder(self, 200, {"status": "ok"})
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.split("?")[0] == "/api/verificar":
            Funcao.do_POST(self)
        else:
            self.send_error(404)

    def _responder(self, status, corpo):
        Funcao._responder(self, status, corpo)

    def log_message(self, formato, *args):  # registro curto, sem corpo da requisição
        sys.stderr.write(f"{self.command} {self.path.split('?')[0]} {args[1] if len(args) > 1 else ''}\n")


def criar_servidor(host, porta):
    return ThreadingHTTPServer((host, porta), partial(Hubstree, directory=str(PUBLICO)))


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    porta = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else 8000))
    servidor = criar_servidor(host, porta)
    print(f"Hubstree em http://{host}:{porta}", flush=True)
    servidor.serve_forever()
