"""
GuruDev — funcoes nativas e metodos de String/Array.

Recuperado do commit 907104d (v15-v18), que existia antes da reescrita
do interpretador em baac865. Mantido em modulo proprio para ser
acrescentado ao interpretador atual sem alterar sua estrutura.
"""

import hashlib
import json
import math
from typing import Any, Dict

from .instancia import Instancia


def _eh_instancia(valor) -> bool:
    """Instancia de classe GuruDev (dict com __classe__)."""
    return isinstance(valor, dict) and "__classe__" in valor


# ============================================================
# FUNCOES NATIVAS
# ============================================================


class Builtins:
    """
    Funcoes nativas do GuruDev.
    Registradas automaticamente no escopo global.
    """

    @staticmethod
    def escrever(*args) -> None:
        """escrever(...) — imprime no stdout."""
        partes = [Builtins._repr(a) for a in args]
        print(" ".join(partes))
        return None

    @staticmethod
    def imprimir(*args) -> None:
        """imprimir(...) — alias para escrever."""
        return Builtins.escrever(*args)

    @staticmethod
    def tipo_de(valor) -> str:
        """tipo_de(valor) — retorna o tipo do valor como string."""
        if valor is None:
            return "Void"
        if isinstance(valor, bool):
            return "Bool"
        if isinstance(valor, int):
            return "Int"
        if isinstance(valor, float):
            return "Float"
        if isinstance(valor, str):
            return "String"
        if isinstance(valor, list):
            return "Array"
        if isinstance(valor, Instancia):
            return valor.classe
        if _eh_instancia(valor):
            return valor["__classe__"]
        if isinstance(valor, dict):
            return "Object"
        return type(valor).__name__

    @staticmethod
    def hash_guru(valor) -> str:
        """hash(valor) — retorna hash SHA-256 do valor."""
        texto = Builtins._repr(valor)
        return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def tamanho(valor) -> int:
        """tamanho(valor) — retorna o tamanho."""
        if isinstance(valor, (str, list, dict)):
            return len(valor)
        raise TypeError(f"tipo_de({Builtins.tipo_de(valor)}) nao suporta tamanho().")

    @staticmethod
    def converter_int(valor) -> int:
        return int(valor)

    @staticmethod
    def converter_float(valor) -> float:
        return float(valor)

    @staticmethod
    def converter_string(valor) -> str:
        return str(valor)

    @staticmethod
    def converter_bool(valor) -> bool:
        return bool(valor)

    @staticmethod
    def ler_entrada() -> str:
        return input()

    @staticmethod
    def para_json(valor) -> str:
        return json.dumps(
            Builtins._to_json_serializable(valor), ensure_ascii=False, indent=2
        )

    @staticmethod
    def de_json(texto: str):
        return json.loads(texto)

    @staticmethod
    def randint(inicio: int, fim: int) -> int:
        import random

        return random.randint(inicio, fim)

    @staticmethod
    def raiz(valor, indice: float = 2.0) -> float:
        return valor ** (1.0 / indice)

    @staticmethod
    def absoluto(valor) -> float:
        return abs(valor)

    @staticmethod
    def arredondar(valor, casas: int = 0) -> float:
        return float(round(valor, casas))

    # --- Helpers internos ---

    @staticmethod
    def _repr(valor) -> str:
        """Representacao para impressao."""
        if valor is None:
            return "nulo"
        if isinstance(valor, bool):
            return "verdadeiro" if valor else "falso"
        if isinstance(valor, str):
            return valor
        if isinstance(valor, float) and valor == int(valor):
            return str(int(valor))
        return repr(valor)

    @staticmethod
    def _to_json_serializable(valor):
        if isinstance(valor, list):
            return [Builtins._to_json_serializable(v) for v in valor]
        if isinstance(valor, dict):
            return {k: Builtins._to_json_serializable(v) for k, v in valor.items()}
        return valor

    @staticmethod
    def registro() -> Dict[str, Any]:
        """Retorna dicionario com todas as builtins prontas para registro."""
        return {
            "escrever": Builtins.escrever,
            "imprimir": Builtins.imprimir,
            "tipo_de": Builtins.tipo_de,
            "hash": Builtins.hash_guru,
            "tamanho": Builtins.tamanho,
            "converter_int": Builtins.converter_int,
            "converter_float": Builtins.converter_float,
            "converter_string": Builtins.converter_string,
            "converter_bool": Builtins.converter_bool,
            "ler_entrada": Builtins.ler_entrada,
            "para_json": Builtins.para_json,
            "de_json": Builtins.de_json,
            "randint": Builtins.randint,
            "raiz": Builtins.raiz,
            "absoluto": Builtins.absoluto,
            "arredondar": Builtins.arredondar,
            "seno": math.sin,
            "cosseno": math.cos,
            "tangente": math.tan,
            "logaritmo": math.log,
            "potencia": math.pow,
            "pi": math.pi,
            "euler": math.e,
            "maximo": max,
            "minimo": min,
        }


# ============================================================
# 4. STRING METHOD DISPATCHER
# ============================================================


class StringMethods:
    """Dispatch de metodos de string em GuruDev."""

    _METHODS = {}

    @classmethod
    def dispatch(cls, obj_str: str, metodo: str, args: list) -> Any:
        handler = cls._METHODS.get(metodo)
        if handler:
            return handler(obj_str, *args)
        raise AttributeError(f"Metodo '{metodo}' nao existe em String.")

    @classmethod
    def register(cls, name):
        def decorator(fn):
            cls._METHODS[name] = fn
            return fn

        return decorator


# Register all string methods


@StringMethods.register("tamanho")
def _str_tamanho(s: str) -> int:
    return len(s)


@StringMethods.register("length")
def _str_length(s: str) -> int:
    return len(s)


@StringMethods.register("maiusculo")
def _str_maiusculo(s: str) -> str:
    return s.upper()


@StringMethods.register("minusculo")
def _str_minusculo(s: str) -> str:
    return s.lower()


@StringMethods.register("dividir")
def _str_dividir(s: str, sep: str = " ") -> list:
    return s.split(sep)


@StringMethods.register("substring")
def _str_substring(s: str, inicio: int, fim: int = -1) -> str:
    if fim == -1 or fim is None:
        return s[inicio:]
    return s[inicio:fim]


@StringMethods.register("trim")
def _str_trim(s: str) -> str:
    return s.strip()


@StringMethods.register("contem")
def _str_contem(s: str, sub: str) -> bool:
    return sub in s


@StringMethods.register("substituir")
def _str_substituir(s: str, antigo: str, novo: str) -> str:
    return s.replace(antigo, novo)


@StringMethods.register("indice")
def _str_indice(s: str, sub: str) -> int:
    return s.find(sub)


@StringMethods.register("repetir")
def _str_repetir(s: str, n: int) -> str:
    return s * n


@StringMethods.register("vazio")
def _str_vazio(s: str) -> bool:
    return len(s) == 0


@StringMethods.register("maiusculo_primeiro")
def _str_capitalize(s: str) -> str:
    if not s:
        return s
    return s[0].upper() + s[1:]


@StringMethods.register("minusculo_primeiro")
def _str_lower_first(s: str) -> str:
    if not s:
        return s
    return s[0].lower() + s[1:]


@StringMethods.register("inverter")
def _str_reverse(s: str) -> str:
    return s[::-1]


@StringMethods.register("comeca_com")
def _str_startswith(s: str, prefixo: str) -> bool:
    return s.startswith(prefixo)


@StringMethods.register("termina_com")
def _str_endswith(s: str, sufixo: str) -> bool:
    return s.endswith(sufixo)


@StringMethods.register("ultimo_indice")
def _str_rfind(s: str, sub: str) -> int:
    return s.rfind(sub)


# ============================================================
# 5. ARRAY METHOD DISPATCHER
# ============================================================


class ArrayMethods:
    """Dispatch de metodos de array em GuruDev."""

    _METHODS = {}

    @classmethod
    def dispatch(cls, obj_list: list, metodo: str, args: list) -> Any:
        handler = cls._METHODS.get(metodo)
        if handler:
            return handler(obj_list, *args)
        raise AttributeError(f"Metodo '{metodo}' nao existe em Array.")

    @classmethod
    def register(cls, name):
        def decorator(fn):
            cls._METHODS[name] = fn
            return fn

        return decorator


# Register all array methods


@ArrayMethods.register("tamanho")
def _arr_tamanho(arr: list) -> int:
    return len(arr)


@ArrayMethods.register("length")
def _arr_length(arr: list) -> int:
    return len(arr)


@ArrayMethods.register("adicionar")
def _arr_adicionar(arr: list, item) -> None:
    arr.append(item)
    return None


@ArrayMethods.register("push")
def _arr_push(arr: list, item) -> None:
    arr.append(item)
    return None


@ArrayMethods.register("remover_ultimo")
def _arr_remover_ultimo(arr: list):
    if not arr:
        raise RuntimeError("remover_ultimo() em array vazio.")
    return arr.pop()


@ArrayMethods.register("pop")
def _arr_pop(arr: list):
    if not arr:
        raise RuntimeError("pop() em array vazio.")
    return arr.pop()


@ArrayMethods.register("contem")
def _arr_contem(arr: list, item) -> bool:
    return item in arr


@ArrayMethods.register("ordenar")
def _arr_ordenar(arr: list) -> list:
    arr.sort()
    return arr


@ArrayMethods.register("juntar")
def _arr_juntar(arr: list, sep: str = ", ") -> str:
    return Builtins._repr(sep).join(Builtins._repr(x) for x in arr)


@ArrayMethods.register("remover")
def _arr_remover(arr: list, item) -> None:
    if item in arr:
        arr.remove(item)
    return None


@ArrayMethods.register("inserir")
def _arr_inserir(arr: list, indice: int, item) -> None:
    arr.insert(indice, item)
    return None


@ArrayMethods.register("inverter")
def _arr_inverter(arr: list) -> list:
    arr.reverse()
    return arr


@ArrayMethods.register("vazio")
def _arr_vazio(arr: list) -> bool:
    return len(arr) == 0


@ArrayMethods.register("fatia")
def _arr_fatia(arr: list, inicio: int, fim: int = -1) -> list:
    if fim == -1 or fim is None:
        return arr[inicio:]
    return arr[inicio:fim]


@ArrayMethods.register("primeiro")
def _arr_primeiro(arr: list):
    if not arr:
        raise RuntimeError("primeiro() em array vazio.")
    return arr[0]


@ArrayMethods.register("ultimo")
def _arr_ultimo(arr: list):
    if not arr:
        raise RuntimeError("ultimo() em array vazio.")
    return arr[-1]


@ArrayMethods.register("indice")
def _arr_indice(arr: list, item) -> int:
    return arr.index(item)


@ArrayMethods.register("limpar")
def _arr_limpar(arr: list) -> None:
    arr.clear()
    return None


@ArrayMethods.register("copiar")
def _arr_copiar(arr: list) -> list:
    return list(arr)


@ArrayMethods.register("mapear")
def _arr_map(arr: list, func) -> list:
    return [func(x) for x in arr]


@ArrayMethods.register("filtrar")
def _arr_filtrar(arr: list, func) -> list:
    return [x for x in arr if func(x)]
