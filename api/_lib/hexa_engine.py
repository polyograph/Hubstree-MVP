"""Engine hexarrelacional π√f(A) — porte em Python do hexa-engine.ts do HexaSign Lab.

Mesmas heurísticas e os mesmos coeficientes do original
(guilherme-machado-ceo/hubstry-hexasign-lab, src/lib/hexa-engine.ts).
O servidor recalcula o vetor de forma independente do navegador e compara.

Limite: as heurísticas são determinísticas e experimentais. Não constituem
instrumento de medição científica validado.
"""

import math
import re
import unicodedata

PHI = (1 + math.sqrt(5)) / 2
RELACOES = ("similitude", "homology", "equivalence", "symmetry", "equilibrium", "compensation")

_CONECTORES = re.compile(r"\b(portanto|logo|assim|se|entao|quando|porque|pois|implica|caso)\b", re.ASCII)
_ESTRUTURAIS = re.compile(r"\b(algoritmo|matriz|sistema|operador|estrutura|funcao|relacao|rede|processo|regra|modelo)\b", re.ASCII)
_CONTRASTE = re.compile(r"\b(mas|porem|porém|embora|enquanto|complementar|compensacao|emergencia|emergente)\b", re.ASCII)


def _normalizar(texto):
    # Mesmo recorte do original em JS: remove só o bloco U+0300–U+036F.
    sem_acento = "".join(c for c in unicodedata.normalize("NFD", texto) if not 0x300 <= ord(c) <= 0x36F)
    return sem_acento.lower()


def golden_norm(vetor):
    return math.sqrt(sum((PHI ** i) * v * v for i, v in enumerate(vetor)))


def pi_sqrt(norma):
    return norma ** (1 / math.pi) if norma > 0 else 0.0


def contar(texto):
    """Contagens usadas pelo engine. re.ASCII espelha o \\b do JavaScript."""
    n = _normalizar(texto)
    palavras = [p for p in re.split(r"\s+", n) if p]
    sentencas = [s.strip() for s in re.split(r"[.!?]+", n) if s.strip()]
    return {
        "palavras": len(palavras),
        "unicas": len(set(palavras)),
        "sentencas": len(sentencas),
        "conectores": len(_CONECTORES.findall(n)),
        "estruturais": len(_ESTRUTURAIS.findall(n)),
        "contraste": len(_CONTRASTE.findall(n)),
    }


def analisar(texto):
    if not isinstance(texto, str) or not texto.strip():
        return {k: 0.0 for k in RELACOES} | {"goldenNorm": 0.0, "piSqrtScore": 0.0}
    c = contar(texto)
    diversidade = c["unicas"] / c["palavras"] if c["palavras"] else 0.0
    comprimento = min(1.0, c["palavras"] / 60)
    v = {
        "similitude": min(1.0, 0.20 + comprimento * 0.55 + diversidade * 0.25),
        "homology": min(1.0, 0.25 + c["estruturais"] / 8),
        "equivalence": min(1.0, 0.25 + c["conectores"] / 6 + diversidade * 0.15),
        "symmetry": min(1.0, 0.20 + min(c["sentencas"], 8) / 12 + c["conectores"] / 12),
        "equilibrium": max(0.0, min(1.0, 0.85 - abs(0.5 - diversidade) * 0.7 - abs(0.5 - comprimento) * 0.25)),
        "compensation": min(1.0, 0.20 + c["contraste"] / 5 + c["estruturais"] / 12),
    }
    norma = golden_norm([v[k] for k in RELACOES])
    return v | {"goldenNorm": norma, "piSqrtScore": pi_sqrt(norma)}
