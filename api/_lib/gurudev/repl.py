#!/usr/bin/env python3
"""
GuruDev REPL - Read-Eval-Print Loop
Prompt interativo para experimentar GuruDev.
"""

import sys


class GuruDevRepl:
    """REPL interativo para GuruDev."""

    BANNER = [
        "",
        "  GuruDev REPL v0.1.0-alpha",
        "  Hubstry-DeepTech",
        "",
        '  Digite codigo GuruDev. "sair" para encerrar.',
        "",
    ]

    def __init__(self, debug=False):
        self.debug = debug
        self.interp = None
        self._multiline_buffer = []

    def run(self):
        for line in self.BANNER:
            print(line)

        while True:
            prompt = "gurudev> " if not self._multiline_buffer else "...      "

            try:
                line = input(prompt)
            except (EOFError, KeyboardInterrupt):
                print()
                break

            # Comandos do REPL
            stripped = line.strip()
            if stripped == "sair" and not self._multiline_buffer:
                break
            if stripped == "limpar" and not self._multiline_buffer:
                self._init_interpreter()
                print("(interpreter reiniciado)")
                continue

            if not stripped:
                if self._multiline_buffer:
                    # Linha vazia finaliza o bloco
                    code = "\n".join(self._multiline_buffer)
                    self._multiline_buffer = []
                    self._exec(code)
                continue

            # Detectar se precisa de mais linhas
            if self._needs_more(stripped):
                self._multiline_buffer.append(stripped)
                continue

            if self._multiline_buffer:
                self._multiline_buffer.append(stripped)
                code = "\n".join(self._multiline_buffer)
                self._multiline_buffer = []
            else:
                code = stripped

            self._exec(code)

    def _init_interpreter(self):
        from src.interpreter import GuruDevInterpreter
        self.interp = GuruDevInterpreter(debug=self.debug)

    def _exec(self, code):
        from src.parser import parse

        # Injetar ; automaticamente se nao termina com ; ou }
        s = code.rstrip()
        if not s.endswith(";") and not s.endswith("}") and not s.endswith("!/codigo!") and not s.endswith("?/python?"):
            code = s + ";"

        try:
            ast = parse(code, debug=False)
            if ast is None:
                print("  Erro: parsing falhou.")
                return

            if self.interp is None:
                self._init_interpreter()

            self.interp.interpretar(ast)

        except Exception as e:
            print(f"  {type(e).__name__}: {e}")

    def _needs_more(self, line):
        """Verifica se a linha abriu algo que precisa ser fechado."""
        # Contar delimitadores abertos
        opens = line.count("{") + line.count("(") + line.count("[")
        closes = line.count("}") + line.count(")") + line.count("]")
        if opens > closes:
            return True
        # Linha termina com operador (continuacao)
        if line.endswith(("->", "+", "-", "*", ",")):
            return True
        return False
