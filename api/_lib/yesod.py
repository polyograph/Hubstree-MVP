"""Yesod: recalcula indicadores no servidor e aplica a politica GuruDev.

Desenho herdado do Evidence Gate da GuruDev (gurudev-core/evidence_gate):
indicadores tipados (bool/int) -> politica .guru estatica -> veredito.

Falha fechada: indicador ausente, extra ou de tipo errado; erro do
interpretador; veredito fora da lista -> BLOQUEADO.
"""

import math
import sys
import threading
from pathlib import Path

AQUI = Path(__file__).resolve().parent
if str(AQUI) not in sys.path:
    sys.path.insert(0, str(AQUI))

from hexa_engine import RELACOES, _aparar, analisar, contar  # noqa: E402

ARQUIVO_POLITICA = AQUI / "politica_hubstree.guru"
LIMITE_CARACTERES = 20_000
TOLERANCIA = 1e-9
VEREDITOS = ("BLOQUEADO", "AMOSTRA_INSUFICIENTE", "LEITURA_LIMITADA", "PROCESSADO")
INDICADORES_BOOL = ("entrada_vazia", "entrada_excede_limite", "vetor_invalido", "divergencia_engine",
                    "vetor_cliente_invalido")
INDICADORES_INT = ("palavras", "sentencas", "componentes_saturados")
_TRAVA = threading.Lock()  # o parser (PLY) nao e reentrante


def vetor_cliente_valido(vetor):
    """Contrato estrito: objeto com exatamente as seis chaves, cada valor um número
    finito em [0,1] do tipo int ou float (bool e strings são recusados)."""
    if not isinstance(vetor, dict) or set(vetor) != set(RELACOES):
        return False
    for k in RELACOES:
        v = vetor[k]
        if type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1:
            return False
    return True


def indicadores(texto, vetor_cliente=None):
    """Devolve (indicadores, metricas_servidor). Nunca executa o texto."""
    if not isinstance(texto, str):
        texto = ""
    vazio = not _aparar(texto)
    excede = len(texto) > LIMITE_CARACTERES
    base = texto[:LIMITE_CARACTERES]
    m = analisar(base)
    c = contar(base) if not vazio else {"palavras": 0, "sentencas": 0}
    valores = [m[k] for k in RELACOES]
    invalido = any((not math.isfinite(v)) or v < 0 or v > 1 for v in valores)
    cliente_invalido = vetor_cliente is not None and not vetor_cliente_valido(vetor_cliente)
    divergente = False
    if vetor_cliente is not None and not cliente_invalido and not vazio:
        divergente = any(abs(vetor_cliente[k] - m[k]) > TOLERANCIA for k in RELACOES)
    ind = {
        "entrada_vazia": vazio,
        "entrada_excede_limite": excede,
        "vetor_invalido": invalido,
        "divergencia_engine": divergente,
        "vetor_cliente_invalido": cliente_invalido,
        "palavras": int(c["palavras"]),
        "sentencas": int(c["sentencas"]),
        "componentes_saturados": sum(1 for v in valores if v >= 1 - TOLERANCIA),
    }
    return ind, m


def _bloqueado(motivo):
    return {"veredito": "BLOQUEADO", "motivo": motivo, "politica_ok": False}


def validar(ind):
    esperados = set(INDICADORES_BOOL) | set(INDICADORES_INT)
    if not isinstance(ind, dict) or set(ind) != esperados:
        raise ValueError("conjunto de indicadores inesperado")
    for n in INDICADORES_BOOL:
        if type(ind[n]) is not bool:
            raise ValueError(f"{n} deve ser bool")
    for n in INDICADORES_INT:
        if type(ind[n]) is not int or ind[n] < 0:
            raise ValueError(f"{n} deve ser int >= 0")


def decidir(ind, fonte_politica=None):
    try:
        validar(ind)
    except ValueError as e:
        return _bloqueado(f"indicadores invalidos: {e}")
    try:
        from gurudev.interpreter import Interpreter
        from gurudev.parser import parse

        codigo = fonte_politica or ARQUIVO_POLITICA.read_text("utf-8")
        with _TRAVA:
            interp = Interpreter()
            for nome, valor in ind.items():
                interp.env.decl(nome, valor)
            interp.interpretar(parse(codigo))
            veredito = interp.env.get("veredito")
            motivo = interp.env.get("motivo")
    except Exception as e:  # erro da linguagem ou do interpretador
        return _bloqueado(f"falha ao executar a politica: {type(e).__name__}")
    if veredito not in VEREDITOS or not isinstance(motivo, str):
        return _bloqueado("a politica produziu um veredito desconhecido")
    return {"veredito": veredito, "motivo": motivo, "politica_ok": True}


def avaliar(texto, vetor_cliente=None):
    ind, m = indicadores(texto, vetor_cliente)
    return {**decidir(ind), "indicadores": ind, "metricas_servidor": m,
            "politica": ARQUIVO_POLITICA.name, "motor": "GuruDev (interpretador real)"}
