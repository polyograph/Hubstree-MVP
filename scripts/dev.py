"""Servidor local: serve public/ e encaminha POST /api/verificar para a função.

Uso: python3 scripts/dev.py  ->  http://127.0.0.1:8000
"""

import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "api"))

from verificar import handler as Funcao  # noqa: E402


class Dev(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path.split("?")[0] == "/api/verificar":
            Funcao.do_POST(self)
        else:
            self.send_error(404)

    def _responder(self, status, corpo):
        Funcao._responder(self, status, corpo)


if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    servidor = ThreadingHTTPServer(("127.0.0.1", porta), partial(Dev, directory=str(RAIZ / "public")))
    print(f"Hubstree em http://127.0.0.1:{porta}")
    servidor.serve_forever()
