#!/usr/bin/env python3
"""
GuruDev® CLI — Interface de linha de comando
Uso:
    gurudev run arquivo.guru [--debug]
    gurudev repl [--debug]
    gurudev --version
    gurudev test
"""

import sys
import os

# Garante que o diretorio do repo esta no path (para rodar sem pip install)
_repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _repo_dir not in sys.path:
    sys.path.insert(0, _repo_dir)


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("help", "-h", "--help"):
        _print_help()
        return

    if args[0] in ("-v", "--version"):
        print("GuruDev v0.1.0-alpha (Hubstry-DeepTech)")
        return

    if args[0] == "run":
        _run_file(args[1:])
        return

    if args[0] == "repl":
        _run_repl(args[1:])
        return

    if args[0] == "test":
        _run_tests()
        return

    # Default: treat as file path
    if args[0].endswith(".guru"):
        _run_file(args)
        return

    print(f"gurudev: comando desconhecido '{args[0]}'")
    print("Digite 'gurudev help' para ajuda.")
    sys.exit(1)


def _print_help():
    print()
    print("  GuruDev® — Linguagem Ontologica de Programacao")
    print("  Hubstry-DeepTech | v0.1.0-alpha")
    print()
    print("  Uso:")
    print("    gurudev run <arquivo.guru>   Executa um arquivo .guru")
    print("    gurudev repl                Inicia o REPL interativo")
    print("    gurudev test                Roda a suite de testes")
    print("    gurudev --version           Mostra a versao")
    print("    gurudev help                Mostra esta ajuda")
    print()
    print("  Exemplos:")
    print('    gurudev run hello.guru')
    print('    gurudev run calc.guru --debug')
    print('    gurudev repl')
    print()


def _run_file(args):
    if not args or args[0].startswith("-"):
        filepath = None
        extra = args
    else:
        filepath = args[0]
        extra = args[1:]

    debug = "--debug" in extra

    if not filepath:
        print("gurudev run: especifique um arquivo .guru")
        print("Uso: gurudev run <arquivo.guru>")
        sys.exit(1)

    if not os.path.exists(filepath):
        print(f"gurudev: arquivo '{filepath}' nao encontrado.")
        sys.exit(1)

    if not filepath.endswith(".guru"):
        print(f"gurudev: esperado arquivo .guru, got '{filepath}'")
        sys.exit(1)

    from src.parser import parse
    from src.interpreter import Interpreter

    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    ast = parse(source, debug=debug)
    if ast is None:
        print("gurudev: falha no parsing — AST vazia.")
        sys.exit(1)

    interp = Interpreter()
    try:
        interp.interpretar(ast)
    except Exception as e:
        print(f"gurudev: erro em runtime — {type(e).__name__}: {e}")
        sys.exit(1)
    # ---- Quantum Output: R5 + R6 + QuantumResult ----
    if interp.significance_vectors or interp.quantum_results:
        for sv in interp.significance_vectors:
            if 'r6_hexarrelacional' in sv and not interp.quantum_results:
                qr = interp.dispatch_quantico(
                    operacao='quantum_' + (sv.get('gm_paradigma') or 'unknown'),
                    nome=sv.get('gm_paradigma'),
                    n_qubits=2,
                    shots=1024,
                )
        print()
        print('=' * 60)
        print('  GuruDev (R) Quantum Results')
        print('=' * 60)
        for i, sv in enumerate(interp.significance_vectors):
            print(f'\n[Bloco {i+1}] R5 (Vetor de Significancia):')
            print(f'  vector:  {sv["vector"]}')
            print(f'  norm:    {sv["norm"]}')
            print(f'  gm:      ontologia={sv["gm_ontologia"]} | campo={sv["gm_campo"]} | '
                  f'hermeneutica={sv["gm_hermeneutica"]} | tempo={sv["gm_tempo"]} | '
                  f'paradigma={sv["gm_paradigma"]}')
            if 'r6_hexarrelacional' in sv:
                print(f'  R6 (Hexarrelacional): {sv["r6_hexarrelacional"]}')
                print(f'  R6 norm:   {sv["r6_norm"]}')
                print(f'  R6 fonte:  {sv["r6_fonte"]}')
        for i, qr in enumerate(interp.quantum_results):
            print(f'\n[QR {i+1}] QuantumResult:')
            print(f'  operacao:      {qr.operacao}')
            print(f'  delegacao:     {qr.delegacao_tipo}')
            print(f'  entropy:       {qr.entropy:.6f}')
            print(f'  distribution:  {qr.distribution}')
            print(f'  most_likely:   {qr.most_likely()}')
            if qr.is_error:
                print(f'  ERRO:          {qr.erro}')
        print()
def _run_repl(args):
    from src.repl import GuruDevRepl
    debug = "--debug" in args
    repl = GuruDevRepl(debug=debug)
    repl.run()


def _run_tests():
    # Busca run_interpreter_test.py no repo
    test_file = os.path.join(_repo_dir, "run_interpreter_test.py")
    if not os.path.exists(test_file):
        print("gurudev: run_interpreter_test.py nao encontrado.")
        sys.exit(1)
    import subprocess
    result = subprocess.run([sys.executable, test_file])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
