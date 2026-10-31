"""Gera tests/unicode_amostras.json: amostras determinísticas para a paridade JS/Python.

Cobre marcas combinantes dentro e fora do bloco U+0300–U+036F, escritas com
decomposição NFD (hangul, vietnamita), RTL, CJK, emoji com ZWJ, sigma final,
I com ponto (turco), ligaduras de compatibilidade, controles e espaços Unicode.
Rodar de novo só muda o arquivo se a semente, a lista ou a base Unicode do Python mudar.
"""

import json
import random
import unicodedata
from pathlib import Path

SEMENTE = 20261031
FAIXAS = [
    (0x0300, 0x036F),  # diacríticos combinantes (removidos pelo engine)
    (0x1AB0, 0x1AFF),  # diacríticos combinantes estendidos (fora do recorte)
    (0x1DC0, 0x1DFF),  # suplemento de diacríticos combinantes
    (0x20D0, 0x20FF),  # diacríticos para símbolos
    (0xFE20, 0xFE2F),  # meias marcas combinantes
    (0x0591, 0x05C7),  # pontuação vocálica hebraica
    (0x064B, 0x065F),  # harakat árabes
    (0x0900, 0x097F),  # devanágari (com matras)
    (0xAC00, 0xD7A3),  # sílabas hangul (decompõem em NFD)
    (0x1E00, 0x1EFF),  # latim estendido adicional (vietnamita)
    (0x0370, 0x03FF),  # grego
    (0x0400, 0x04FF),  # cirílico
    (0x4E00, 0x9FFF),  # ideogramas CJK
    (0x2000, 0x200F),  # espaços e marcas de largura zero
    (0x1F300, 0x1FAFF),  # emoji
    (0xFB00, 0xFB06),  # ligaduras (fi, fl...)
]
FIXOS = [
    "İstanbul İ ı ΣΟΦΙΑ σοφίας ΟΔΟΣ ß ẞ ﬁm ﬂor",
    "Ações e operações: o sistema, porém, compensa. Então se repete? Sim!",
    "é vs é; a᪰b c⃗d x̶y z︠w",
    "👩‍💻 família 👨‍👩‍👧 regra​processo modelo rede",
    "Tiếng Việt có dấu: người, được, những. 한국어 문장입니다. עִבְרִית. العَرَبِيَّة.",
    "linha1\nlinha2\tcoluna\r\nfim sep par\u0085nel",
]
PALAVRAS = ["sistema", "regra", "porém", "então", "relação", "função", "mas", "se", "embora", "modelo", "rede", "processo"]


def caractere(rng, ini, fim, atribuido):
    while True:
        c = chr(rng.randint(ini, fim))
        if not atribuido or unicodedata.category(c) != "Cn":
            return c


def amostra(rng, atribuido=True, faixas=FAIXAS):
    partes = []
    for _ in range(rng.randint(3, 18)):
        if rng.random() < 0.4:
            partes.append(rng.choice(PALAVRAS))
        else:
            ini, fim = rng.choice(faixas)
            partes.append("".join(caractere(rng, ini, fim, atribuido) for _ in range(rng.randint(1, 6))))
        partes.append(rng.choice([" ", " ", " ", ". ", "! ", "? ", "　", " ", "\n"]))
    return "".join(partes)


def main():
    rng = random.Random(SEMENTE)
    # 400 amostras só com caracteres atribuídos (paridade exigida) e 40 com marcas
    # recentes ou ainda não atribuídas (onde a ordem NFD pode variar entre runtimes).
    recentes = [(0x1AB0, 0x1AFF), (0x20D0, 0x20FF), (0x1F300, 0x1FAFF)]
    amostras = (FIXOS + [amostra(rng) for _ in range(400)]
                + [amostra(rng, atribuido=False, faixas=recentes) for _ in range(40)])
    destino = Path(__file__).resolve().parent / "unicode_amostras.json"
    destino.write_text(json.dumps(amostras, ensure_ascii=True, indent=0), "utf-8")
    print(f"{len(amostras)} amostras em {destino.name}")


if __name__ == "__main__":
    main()
