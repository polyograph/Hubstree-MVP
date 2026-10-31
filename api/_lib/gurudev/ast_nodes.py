"""
GuruDev AST Nodes v1.1.0-alpha
Definicao dos nos da Arvore Sintatico-Semantica (AST)
Autor: Guilherme Goncalves Machado
Hubstry-DeepTech

v1.1 changes: Added PropAtribuicao (property assignment)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any


# ============================================================
# BASE
# ============================================================

@dataclass
class Node:
    """No base da AST. Todos os nos herdam deste."""
    lineno: int = 0
    gm_ontologia: Optional[str] = None
    gm_campo: Optional[str] = None
    gm_hermeneutica: Optional[str] = None
    gm_tempo: Optional[str] = None
    gm_paradigma: Optional[str] = None


# ============================================================
# PROGRAMA
# ============================================================

@dataclass
class Programa(Node):
    """No raiz: o programa completo."""
    elementos: List[Node] = field(default_factory=list)


# ============================================================
# BLOCO TRIPLO
# ============================================================

@dataclass
class Sobrescrita(Node):
    """Metadados semanticos do bloco."""
    contextos: List[str] = field(default_factory=list)
    nivel: Optional[str] = None
    raiz: Optional[str] = None
    clave: Optional[str] = None
    ontologia: Optional[str] = None
    paradigma: Optional[str] = None


@dataclass
class SubescritaLinguagem(Node):
    """Codigo em linguagem estrangeira."""
    linguagem: str = ""
    conteudo: str = ""
    tipo_mapeamento: Optional[str] = None
    conversao: Optional[str] = None


@dataclass
class Bloco(Node):
    """Bloco triplo: sobrescrita + codigo + subescritas."""
    sobrescrita: Optional[Sobrescrita] = None
    codigo: List[Node] = field(default_factory=list)
    subescritas: List[SubescritaLinguagem] = field(default_factory=list)
    compensacao: Optional['BlocoCompensacao'] = None
    plastico: Optional['BlocoPlastico'] = None
    modulacao: Optional['BlocoModulacao'] = None


# ============================================================
# BLOCOS DE INTEROPERABILIDADE
# ============================================================

@dataclass
class BlocoErro(Node):
    tipo_erro: Optional[str] = None
    alvo_subescrita: Optional[str] = None
    corpo: List[Node] = field(default_factory=list)


@dataclass
class BlocoDesempenho(Node):
    estrategia: Optional[str] = None
    alvo_subescrita: Optional[str] = None
    corpo: List[Node] = field(default_factory=list)


@dataclass
class BlocoAlternativa(Node):
    condicao: Optional[str] = None
    alvo_subescrita: Optional[str] = None
    corpo: List[Node] = field(default_factory=list)


@dataclass
class BlocoCompensacao(Node):
    erros: List[BlocoErro] = field(default_factory=list)
    desempenhos: List[BlocoDesempenho] = field(default_factory=list)
    alternativas: List[BlocoAlternativa] = field(default_factory=list)


@dataclass
class BlocoPlastico(Node):
    corpo: List[Node] = field(default_factory=list)


@dataclass
class ModulacaoAlvo(Node):
    linguagem: str = ""
    inversao: Optional[str] = None
    corpo: List[Node] = field(default_factory=list)


@dataclass
class BlocoModulacao(Node):
    alvos: List[ModulacaoAlvo] = field(default_factory=list)


# ============================================================
# DECLARACOES E DEFINICOES
# ============================================================

@dataclass
class DeclaracaoVariavel(Node):
    """Ex: String nome = "Guilherme"; """
    tipo: str = ""
    nome: str = ""
    valor: Optional[Node] = None
    caso_gramatical: Optional[str] = None
    modificador_acesso: Optional[str] = None


@dataclass
class DefinicaoFuncao(Node):
    """Ex: NOM funcao calcular(Int x, Int y) -> Float { ... }"""
    nome: str = ""
    parametros: List['Parametro'] = field(default_factory=list)
    tipo_retorno: Optional[str] = None
    corpo: List[Node] = field(default_factory=list)
    caso_gramatical: Optional[str] = None
    modificador_acesso: Optional[str] = None
    classificacao_semantica: Optional[str] = None  # Buhler: puro / efeito / expressao


@dataclass
class Parametro(Node):
    tipo: str = ""
    nome: str = ""
    valor_padrao: Optional[Node] = None  # Tesniere: circunstante (opcional)""


@dataclass
class DefinicaoClasse(Node):
    """Ex: NOM classe Pessoa extends SerVivo implements Autenticavel { ... }"""
    nome: str = ""
    superclasse: Optional[str] = None
    interfaces: List[str] = field(default_factory=list)
    membros: List[Node] = field(default_factory=list)
    caso_gramatical: Optional[str] = None
    modificador_acesso: Optional[str] = None


# ============================================================
# ORACOES DE CODIGO (Statements)
# ============================================================

@dataclass
class Atribuicao(Node):
    """Ex: nome = valor;"""
    alvo: str = ""
    valor: Optional[Node] = None
    caso_gramatical: Optional[str] = None


@dataclass
class PropAtribuicao(Node):
    """Ex: this.x = valor; obj.prop = valor; ou ACU.obj.prop = valor;

    caso_gramatical registra o caso declarado (ACU, NOM...); a execucao e a
    mesma de obj.prop = valor.
    """
    objeto: str = ""
    propriedade: str = ""
    valor: Optional[Node] = None
    caso_gramatical: Optional[str] = None


@dataclass
class Retorno(Node):
    """Ex: return valor; / retorna valor;"""
    valor: Optional[Node] = None


@dataclass
class Break(Node):
    pass


@dataclass
class Continue(Node):
    pass


# ============================================================
# ANOTACOES
# ============================================================

@dataclass
class AnotacaoSemantica(Node):
    """#sem: puro / #sem: efeito / #sem: expressao (Buhler - Organon)"""
    valor: str = ""


# ============================================================
# CONTROLE DE FLUXO
# ============================================================

@dataclass
class Se(Node):
    """if/se - corpo_falso pode ser List[Node] (else) ou Se (elif chain)"""
    condicao: Optional[Node] = None
    corpo_verdadeiro: List[Node] = field(default_factory=list)
    corpo_falso: Any = None  # None | List[Node] | Se (para elif)


@dataclass
class Para(Node):
    """for/para (estilo C)"""
    inicializacao: Optional[Node] = None
    condicao: Optional[Node] = None
    incremento: Optional[Node] = None
    corpo: List[Node] = field(default_factory=list)


@dataclass
class ParaCada(Node):
    """for-each: para (Tipo item : colecao)"""
    tipo: str = ""
    variavel: str = ""
    iteravel: str = ""
    corpo: List[Node] = field(default_factory=list)


@dataclass
class Enquanto(Node):
    """while/enquanto"""
    condicao: Optional[Node] = None
    corpo: List[Node] = field(default_factory=list)


# ============================================================
# EXECUCAO SERIE/PARALELO
# ============================================================

@dataclass
class ExecucaoSerie(Node):
    corpo: List[Node] = field(default_factory=list)


@dataclass
class ExecucaoParalelo(Node):
    corpo: List[Node] = field(default_factory=list)


@dataclass
class ExecucaoEm(Node):
    """em python { ... } / em rust { ... }"""
    linguagem: str = ""
    corpo: List[Node] = field(default_factory=list)


# ============================================================
# PRODUCOES DE VALOR (Expressions)
# ============================================================

@dataclass
class ArrayLiteral(Node):
    """Array literal: [expr1, expr2, ...]"""
    elementos: List[Node] = field(default_factory=list)


@dataclass
class Literal(Node):
    """String, Int, Float, Bool literal"""
    valor: Any = None
    tipo: str = ""


@dataclass
class Identificador(Node):
    nome: str = ""


@dataclass
class ChamadaFuncao(Node):
    """Ex: VOC.minhaFuncao(arg1, arg2)"""
    nome: str = ""
    argumentos: List[Node] = field(default_factory=list)
    caso_gramatical: Optional[str] = None


@dataclass
class ChamadaMetodo(Node):
    """Ex: objeto.metodo(arg1, arg2)"""
    objeto: str = ""
    metodo: str = ""
    argumentos: List[Node] = field(default_factory=list)
    caso_gramatical: Optional[str] = None


@dataclass
class OperacaoBinaria(Node):
    """Ex: a + b, x == y, p && q"""
    esquerda: Optional[Node] = None
    operador: str = ""
    direita: Optional[Node] = None


@dataclass
class OperacaoUnaria(Node):
    """Ex: -x, !flag"""
    operador: str = ""
    operando: Optional[Node] = None


@dataclass
class AcessoPropriedade(Node):
    """Ex: GEN.usuario.nome"""
    objeto: str = ""
    propriedade: str = ""
    caso_gramatical: Optional[str] = None
