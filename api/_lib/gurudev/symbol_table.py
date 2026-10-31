"""
GuruDev® Symbol Table — Versão 1.0.0-alpha
Tabela de Símbolos para a linguagem GuruDev®
Autor: Guilherme Gonçalves Machado

Terminologia:
  - Ambiente = Scope (escopo léxico)
  - Simbolo = Symbol (variável, função, classe)
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ============================================================
# 1. CATEGORIAS DE SÍMBOLOS
# ============================================================

class CategoriaSimbolo(Enum):
    """Categoria ontológica do símbolo (caso gramatical)."""
    VOC = "VOC"    # Vocativo — invocação / chamada
    NOM = "NOM"    # Nominativo — sujeito / definição
    ACU = "ACU"    # Acusativo — objeto direto
    DAT = "DAT"    # Dativo — objeto indireto
    GEN = "GEN"    # Genitivo — posse / propriedade
    INS = "INS"    # Instrumental — meio / ferramenta
    LOC = "LOC"    # Locativo — lugar / contexto
    ABL = "ABL"    # Ablativo — origem / separação


class TipoSimbolo(Enum):
    """Tipo do símbolo na tabela."""
    VARIAVEL = "variavel"
    FUNCAO = "funcao"
    PARAMETRO = "parametro"
    CLASSE = "classe"
    BUILTIN = "builtin"


# ============================================================
# 2. ENTRADA DA TABELA DE SÍMBOLOS
# ============================================================

@dataclass
class EntradaSimbolo:
    """Uma entrada na tabela de símbolos."""
    nome: str
    tipo_simbolo: TipoSimbolo
    tipo_dado: str = ""                     # String, Int, Float, Bool, Void, etc.
    categoria: Optional[CategoriaSimbolo] = None  # VOC, NOM, ACU...
    valor: Any = None
    escopo: Optional['Ambiente'] = None     # referência ao escopo de definição
    readonly: bool = False
    modificador_acesso: Optional[str] = None  # publico, privado, protegido
    parametros: Optional[List['EntradaSimbolo']] = None
    tipo_retorno: Optional[str] = None
    lineno: int = 0


# ============================================================
# 3. AMBIENTE (ESCOPO LÉXICO)
# ============================================================

class Ambiente:
    """
    Ambiente (escopo léxico) — cadeia de escopos para resolução de nomes.
    Implementa lookup dinâmico: busca no escopo atual e nos pais.
    """

    def __init__(self, nome: str = "global", pai: Optional['Ambiente'] = None):
        self.nome = nome
        self.pai = pai
        self._simbolos: Dict[str, EntradaSimbolo] = {}
        self._filhos: List['Ambiente'] = []

    # --- Gerenciamento de escopo ---

    def criar_escopo(self, nome: str) -> 'Ambiente':
        """Cria um escopo filho."""
        filho = Ambiente(nome=nome, pai=self)
        self._filhos.append(filho)
        return filho

    # --- Definição de símbolos ---

    def definir(self, nome: str, tipo_simbolo: TipoSimbolo,
                tipo_dado: str = "", categoria: Optional[str] = None,
                valor: Any = None, readonly: bool = False,
                modificador_acesso: Optional[str] = None,
                parametros: Optional[list] = None,
                tipo_retorno: Optional[str] = None,
                lineno: int = 0) -> EntradaSimbolo:
        """
        Define um novo símbolo no escopo atual.
        Se já existir, sobrescreve (permite redefinição no mesmo escopo).
        """
        cat = None
        if categoria:
            try:
                cat = CategoriaSimbolo[categoria.upper()]
            except KeyError:
                pass

        entrada = EntradaSimbolo(
            nome=nome,
            tipo_simbolo=tipo_simbolo,
            tipo_dado=tipo_dado,
            categoria=cat,
            valor=valor,
            escopo=self,
            readonly=readonly,
            modificador_acesso=modificador_acesso,
            parametros=parametros,
            tipo_retorno=tipo_retorno,
            lineno=lineno,
        )
        self._simbolos[nome] = entrada
        return entrada

    # --- Resolução de símbolos ---

    def resolver(self, nome: str) -> Optional[EntradaSimbolo]:
        """
        Busca um símbolo pelo nome, subindo na cadeia de escopos.
        Retorna None se não encontrado.
        """
        if nome in self._simbolos:
            return self._simbolos[nome]
        if self.pai is not None:
            return self.pai.resolver(nome)
        return None

    def obter(self, nome: str) -> Any:
        """Retorna o valor de um símbolo, ou levanta erro se não encontrado."""
        entrada = self.resolver(nome)
        if entrada is None:
            raise NameError(
                f"Simbolo '{nome}' nao definido no escopo '{self.nome}' "
                f"nem nos escopos superiores."
            )
        return entrada.valor

    # --- Atribuição ---

    def atribuir(self, nome: str, valor: Any) -> None:
        """
        Atribui um valor a um símbolo existente.
        Busca na cadeia de escopos. Levanta erro se não encontrado ou readonly.
        """
        entrada = self.resolver(nome)
        if entrada is None:
            raise NameError(
                f"Simbolo '{nome}' nao definido no escopo '{self.nome}' "
                f"nem nos escopos superiores."
            )
        if entrada.readonly:
            raise RuntimeError(
                f"Simbolo '{nome}' eh readonly (constante)."
            )
        entrada.valor = valor

    # --- Introspecção ---

    def listar(self, incluir_heranca: bool = False) -> Dict[str, EntradaSimbolo]:
        """Lista todos os símbolos do escopo atual (e pais, se solicitado)."""
        if incluir_heranca and self.pai:
            resultado = self.pai.listar(incluir_heranca=True)
        else:
            resultado = {}
        resultado.update(self._simbolos)
        return resultado

    def tem(self, nome: str) -> bool:
        """Verifica se um símbolo existe neste escopo (sem buscar nos pais)."""
        return nome in self._simbolos

    def __repr__(self) -> str:
        return f"Ambiente('{self.nome}', {len(self._simbolos)} simbolos, {len(self._filhos)} filhos)"


# ============================================================
# 4. TABELA DE SÍMBOLOS GLOBAL
# ============================================================

class TabelaDeSimbolos:
    """
    Tabela de Símbolos global — gerencia todos os ambientes (escopos).
    """

    def __init__(self):
        self.global_env = Ambiente(nome="global")
        self._todos_ambientes: List[Ambiente] = [self.global_env]

    def ambiente_atual(self) -> Ambiente:
        """Retorna o escopo global (será sobrescrito pelo interpreter)."""
        return self.global_env

    def registrar(self, ambiente: Ambiente) -> None:
        """Registra um novo ambiente na tabela."""
        self._todos_ambientes.append(ambiente)

    def total_simbolos(self) -> int:
        """Total de símbolos em todos os escopos."""
        return sum(len(env._simbolos) for env in self._todos_ambientes)

    def dump(self) -> str:
        """Representação textual de todos os escopos e símbolos."""
        linhas = ["=== Tabela de Simbolos ==="]
        for env in self._todos_ambientes:
            if not env._simbolos:
                continue
            caminho = self._caminho_escopo(env)
            linhas.append(f"\n  [{caminho}]")
            for nome, sym in env._simbolos.items():
                cat = f" {sym.categoria.value}" if sym.categoria else ""
                acess = f" ({sym.modificador_acesso})" if sym.modificador_acesso else ""
                val_repr = repr(sym.valor)
                if len(val_repr) > 50:
                    val_repr = val_repr[:47] + "..."
                linhas.append(
                    f"    {sym.tipo_simbolo.value:10s} | {sym.tipo_dado:10s} | "
                    f"{nome}{cat}{acess} = {val_repr}"
                )
        return "\n".join(linhas)

    def _caminho_escopo(self, env: Ambiente) -> str:
        """Constroi o caminho do escopo (ex: global > somar > corpo)."""
        partes = []
        atual = env
        while atual:
            partes.append(atual.nome)
            atual = atual.pai
        return " > ".join(reversed(partes))
