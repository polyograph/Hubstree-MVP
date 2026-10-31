"""
GuruDev® Parser — Versão 1.0.0-alpha
Analisador Sintático para a linguagem GuruDev®
Autor: Guilherme Gonçalves Machado
Ferramenta: PLY (Python Lex-Yacc)

Terminologia:
  - oracao_de_codigo = statement (oração computacional)
  - producao_de_valor = expression (produção de valor)

Baseado em: GRAMMAR_V1_0_0_ALPHA.md
"""

import ply.yacc as yacc
from .lexer import tokens, build_lexer
from .ast_nodes import *

# ============================================================
# 1. PRECEDÊNCIA DE OPERADORES
# ============================================================

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQUALS', 'NOT_EQUALS'),
    ('left', 'LESS_THAN', 'GREATER_THAN', 'LESS_EQUAL', 'GREATER_EQUAL'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE', 'MODULO'),
    ('right', 'UMINUS', 'UNOT'),   # unários: -x, !x
)

# ============================================================
# 2. REGRA INICIAL: PROGRAMA (Discurso Pragmático)
# ============================================================

def p_programa(p):
    '''programa : elementos'''
    p[0] = Programa(elementos=p[1], lineno=p.lineno(1))


def p_elementos_multiple(p):
    '''elementos : elementos elemento'''
    p[0] = p[1] + [p[2]]


def p_elementos_single(p):
    '''elementos : elemento'''
    p[0] = [p[1]]


def p_elemento_bloco(p):
    '''elemento : bloco'''
    p[0] = p[1]


def p_elemento_top_level(p):
    '''elemento : oracao_de_codigo'''
    p[0] = p[1]


# ============================================================
# 3. BLOCO TRÍPLICE
# ============================================================


def _propagar_gm(bloco):
    """Propaga coordenadas GuruMatrix do bloco para nos filhos."""
    gm = {}
    if bloco.gm_ontologia: gm["gm_ontologia"] = bloco.gm_ontologia
    if bloco.gm_campo: gm["gm_campo"] = bloco.gm_campo
    if bloco.gm_hermeneutica: gm["gm_hermeneutica"] = bloco.gm_hermeneutica
    if bloco.gm_tempo: gm["gm_tempo"] = bloco.gm_tempo
    if bloco.gm_paradigma: gm["gm_paradigma"] = bloco.gm_paradigma

    def visitar(no):
        if no is None:
            return
        for attr, val in gm.items():
            if getattr(no, attr, None) is None:
                setattr(no, attr, val)
        for fld in getattr(no.__class__, "__dataclass_fields__", {}):
            child = getattr(no, fld, None)
            if isinstance(child, list):
                for item in child:
                    # listas podem conter texto (ex.: interfaces de classe)
                    if isinstance(item, Node):
                        visitar(item)

    for no in bloco.codigo:
        visitar(no)


def p_bloco(p):
    '''bloco : BLOCO_START sobrescrita_opt codigo_block subescritas_opt compensacao_opt BLOCO_END'''
    bloco = Bloco(
        sobrescrita=p[2],
        codigo=p[3],
        subescritas=p[4] if p[4] else [],
        compensacao=p[5],
        lineno=p.lineno(1)
    )
    # Popular coordenadas GuruMatrix a partir da Sobrescrita
    if p[2] is not None:
        sob = p[2]
        bloco.gm_ontologia = sob.ontologia
        bloco.gm_campo = sob.clave
        bloco.gm_hermeneutica = sob.nivel
    # Defaults para dimensoes sem atributo na sobrescrita
    bloco.gm_tempo = 'compilacao'
    if p[2] is not None and getattr(p[2], 'paradigma', None):
        bloco.gm_paradigma = p[2].paradigma
    else:
        bloco.gm_paradigma = 'imperativo'
    # Propagar gm_* para nos filhos do codigo
    _propagar_gm(bloco)
    p[0] = bloco


# --- Sobrescrita ---

def p_sobrescrita_opt_present(p):
    '''sobrescrita_opt : SOBRESCRITA_START sobrescrita_conteudo SOBRESCRITA_END'''
    p[0] = p[2]


def p_sobrescrita_opt_empty(p):
    '''sobrescrita_opt : empty'''
    p[0] = None


def p_sobrescrita_conteudo(p):
    '''sobrescrita_conteudo : sobrescrita_attrs'''
    # Construir Sobrescrita a partir dos atributos coletados
    attrs = p[1]
    sob = Sobrescrita(lineno=p.lineno(1))
    for attr in attrs:
        if attr[0] == 'string':
            sob.contextos.append(attr[1])
        elif attr[0] == 'nivel':
            sob.nivel = attr[1]
        elif attr[0] == 'raiz':
            sob.raiz = attr[1]
        elif attr[0] == 'clave':
            sob.clave = attr[1]
        elif attr[0] == 'ont':
            sob.ontologia = attr[1]
        elif attr[0] == 'paradigma':
            sob.paradigma = attr[1]
    p[0] = sob


def p_sobrescrita_attrs_multiple(p):
    '''sobrescrita_attrs : sobrescrita_attrs sobrescrita_attr'''
    p[0] = p[1] + [p[2]]


def p_sobrescrita_attrs_single(p):
    '''sobrescrita_attrs : sobrescrita_attr'''
    p[0] = [p[1]]


def p_sobrescrita_attr_string(p):
    '''sobrescrita_attr : STRING_LITERAL'''
    p[0] = ('string', p[1])


def p_sobrescrita_attr_nivel(p):
    '''sobrescrita_attr : NIVEL_ATTR'''
    p[0] = ('nivel', p[1])


def p_sobrescrita_attr_nivel_literal(p):
    '''sobrescrita_attr : NIVEL_LITERAL'''
    p[0] = ('nivel', 'literal')


def p_sobrescrita_attr_nivel_holistico(p):
    '''sobrescrita_attr : NIVEL_HOLISTICO'''
    p[0] = ('nivel', 'holistico')

# Regras para todos os 13 niveis hermeneuticos
# Canonicos (1-7): Literal, Alegorico, Moral, Mistico, Funcional, Estetico, Ontologico
# Estendidos (8-13): Holistico, Matematico, Simbolico, Parabolico, Historico, Linguistico
# (NIVEL_LITERAL e NIVEL_HOLISTICO ja tem regras acima)


def p_sobrescrita_attr_nivel_alegorico(p):
    '''sobrescrita_attr : NIVEL_ALEGORICO'''
    p[0] = ('nivel', 'alegorico')


def p_sobrescrita_attr_nivel_moral(p):
    '''sobrescrita_attr : NIVEL_MORAL'''
    p[0] = ('nivel', 'moral')


def p_sobrescrita_attr_nivel_mistico(p):
    '''sobrescrita_attr : NIVEL_MISTICO'''
    p[0] = ('nivel', 'mistico')


def p_sobrescrita_attr_nivel_funcional(p):
    '''sobrescrita_attr : NIVEL_FUNCIONAL'''
    p[0] = ('nivel', 'funcional')


def p_sobrescrita_attr_nivel_estetico(p):
    '''sobrescrita_attr : NIVEL_ESTETICO'''
    p[0] = ('nivel', 'estetico')


def p_sobrescrita_attr_nivel_ontologico(p):
    '''sobrescrita_attr : NIVEL_ONTOLOGICO'''
    p[0] = ('nivel', 'ontologico')


def p_sobrescrita_attr_nivel_matematico(p):
    '''sobrescrita_attr : NIVEL_MATEMATICO'''
    p[0] = ('nivel', 'matematico')


def p_sobrescrita_attr_nivel_simbolico(p):
    '''sobrescrita_attr : NIVEL_SIMBOLICO'''
    p[0] = ('nivel', 'simbolico')


def p_sobrescrita_attr_nivel_parabolico(p):
    '''sobrescrita_attr : NIVEL_PARABOLICO'''
    p[0] = ('nivel', 'parabolico')


def p_sobrescrita_attr_nivel_historico(p):
    '''sobrescrita_attr : NIVEL_HISTORICO'''
    p[0] = ('nivel', 'historico')


def p_sobrescrita_attr_nivel_linguistico(p):
    '''sobrescrita_attr : NIVEL_LINGUISTICO'''
    p[0] = ('nivel', 'linguistico')


def p_sobrescrita_attr_raiz(p):
    '''sobrescrita_attr : RAIZ_ATTR'''
    p[0] = ('raiz', p[1])


def p_sobrescrita_attr_clave(p):
    '''sobrescrita_attr : CLAVE_ATTR'''
    p[0] = ('clave', p[1])


def p_sobrescrita_attr_clave_ciencia(p):
    '''sobrescrita_attr : CLAVE_CIENCIA'''
    p[0] = ('clave', 'ciencia')


def p_sobrescrita_attr_clave_arte(p):
    '''sobrescrita_attr : CLAVE_ARTE'''
    p[0] = ('clave', 'arte')


def p_sobrescrita_attr_clave_filosofia(p):
    '''sobrescrita_attr : CLAVE_FILOSOFIA'''
    p[0] = ('clave', 'filosofia')


def p_sobrescrita_attr_clave_geral(p):
    '''sobrescrita_attr : CLAVE_GERAL'''
    p[0] = ('clave', 'geral')


def p_sobrescrita_attr_ont(p):
    '''sobrescrita_attr : ONT_ATTR'''
    p[0] = ('ont', p[1])


def p_sobrescrita_attr_ont_acao(p):
    '''sobrescrita_attr : ONT_ACAO'''
    p[0] = ('ont', 'acao')

def p_sobrescrita_attr_paradigma(p):
    '''sobrescrita_attr : PARADIGMA_ATTR'''
    p[0] = ('paradigma', p[1])


def p_sobrescrita_attr_paradigma_vqe(p):
    '''sobrescrita_attr : PARADIGMA_VQE'''
    p[0] = ('paradigma', 'vqe')


def p_sobrescrita_attr_paradigma_qaoa(p):
    '''sobrescrita_attr : PARADIGMA_QAOA'''
    p[0] = ('paradigma', 'qaoa')


def p_sobrescrita_attr_paradigma_quantico(p):
    '''sobrescrita_attr : PARADIGMA_QUANTICO'''
    p[0] = ('paradigma', 'quantico')


def p_sobrescrita_attr_paradigma_quantum(p):
    '''sobrescrita_attr : PARADIGMA_QUANTUM'''
    p[0] = ('paradigma', 'quantum')


def p_sobrescrita_attr_paradigma_variacional(p):
    '''sobrescrita_attr : PARADIGMA_VARIACIONAL'''
    p[0] = ('paradigma', 'variacional')


def p_sobrescrita_attr_paradigma_hibrido(p):
    '''sobrescrita_attr : PARADIGMA_HIBRIDO'''
    p[0] = ('paradigma', 'hibrido')


def p_sobrescrita_attr_paradigma_imperativo(p):
    '''sobrescrita_attr : PARADIGMA_IMPERATIVO'''
    p[0] = ('paradigma', 'imperativo')


def p_sobrescrita_attr_paradigma_funcional(p):
    '''sobrescrita_attr : PARADIGMA_FUNCIONAL'''
    p[0] = ('paradigma', 'funcional')


def p_sobrescrita_attr_paradigma_oo(p):
    '''sobrescrita_attr : PARADIGMA_OO'''
    p[0] = ('paradigma', 'orientado_a_objetos')


def p_sobrescrita_attr_paradigma_logico(p):
    '''sobrescrita_attr : PARADIGMA_LOGICO'''
    p[0] = ('paradigma', 'logico')


def p_sobrescrita_attr_paradigma_declarativo(p):
    '''sobrescrita_attr : PARADIGMA_DECLARATIVO'''
    p[0] = ('paradigma', 'declarativo')


# (Adicionar regras para cada ONT_* conforme necessário)


# --- Código GuruDev® ---

def p_codigo_block(p):
    '''codigo_block : CODIGO_START oracoes_opt CODIGO_END'''
    p[0] = p[2]


def p_oracoes_opt_present(p):
    '''oracoes_opt : oracoes'''
    p[0] = p[1]


def p_oracoes_opt_empty(p):
    '''oracoes_opt : empty'''
    p[0] = []


def p_oracoes_multiple(p):
    '''oracoes : oracoes oracao_de_codigo'''
    p[0] = p[1] + [p[2]]


def p_oracoes_single(p):
    '''oracoes : oracao_de_codigo'''
    p[0] = [p[1]]


# --- Subescritas ---

def p_subescritas_opt_present(p):
    '''subescritas_opt : SUBESCRITAS_START subescritas_lista SUBESCRITAS_END'''
    p[0] = p[2]


def p_subescritas_opt_empty(p):
    '''subescritas_opt : empty'''
    p[0] = None


def p_subescritas_lista_multiple(p):
    '''subescritas_lista : subescritas_lista subescrita_item'''
    p[0] = p[1] + [p[2]]


def p_subescritas_lista_single(p):
    '''subescritas_lista : subescrita_item'''
    p[0] = [p[1]]


def p_subescrita_python(p):
    '''subescrita_item : PYTHON_START FOREIGN_CODE_CONTENT PYTHON_END'''
    p[0] = SubescritaLinguagem(linguagem='python', conteudo=p[2], lineno=p.lineno(1))


def p_subescrita_rust(p):
    '''subescrita_item : RUST_START FOREIGN_CODE_CONTENT RUST_END'''
    p[0] = SubescritaLinguagem(linguagem='rust', conteudo=p[2], lineno=p.lineno(1))


def p_subescrita_javascript(p):
    '''subescrita_item : JAVASCRIPT_START FOREIGN_CODE_CONTENT JAVASCRIPT_END'''
    p[0] = SubescritaLinguagem(linguagem='javascript', conteudo=p[2], lineno=p.lineno(1))


def p_subescrita_java(p):
    '''subescrita_item : JAVA_START FOREIGN_CODE_CONTENT JAVA_END'''
    p[0] = SubescritaLinguagem(linguagem='java', conteudo=p[2], lineno=p.lineno(1))


def p_subescrita_csharp(p):
    '''subescrita_item : CSHARP_START FOREIGN_CODE_CONTENT CSHARP_END'''
    p[0] = SubescritaLinguagem(linguagem='csharp', conteudo=p[2], lineno=p.lineno(1))


def p_subescrita_cpp(p):
    '''subescrita_item : CPP_START FOREIGN_CODE_CONTENT CPP_END'''
    p[0] = SubescritaLinguagem(linguagem='c++', conteudo=p[2], lineno=p.lineno(1))


def p_subescrita_sql(p):
    '''subescrita_item : SQL_START FOREIGN_CODE_CONTENT SQL_END'''
    p[0] = SubescritaLinguagem(linguagem='sql', conteudo=p[2], lineno=p.lineno(1))


def p_subescrita_r(p):
    '''subescrita_item : R_START FOREIGN_CODE_CONTENT R_END'''
    p[0] = SubescritaLinguagem(linguagem='r', conteudo=p[2], lineno=p.lineno(1))


def p_subescrita_wasm(p):
    '''subescrita_item : WASM_START FOREIGN_CODE_CONTENT WASM_END'''
    p[0] = SubescritaLinguagem(linguagem='wasm', conteudo=p[2], lineno=p.lineno(1))


# --- Compensação (opcional) ---

def p_compensacao_opt_present(p):
    '''compensacao_opt : COMPENSACAO_START compensacao_conteudo COMPENSACAO_END'''
    p[0] = p[2]


def p_compensacao_opt_empty(p):
    '''compensacao_opt : empty'''
    p[0] = None


def p_compensacao_conteudo(p):
    '''compensacao_conteudo : compensacao_items'''
    comp = BlocoCompensacao(lineno=p.lineno(1))
    for item in p[1]:
        if isinstance(item, BlocoErro):
            comp.erros.append(item)
        elif isinstance(item, BlocoDesempenho):
            comp.desempenhos.append(item)
        elif isinstance(item, BlocoAlternativa):
            comp.alternativas.append(item)
    p[0] = comp


def p_compensacao_items_multiple(p):
    '''compensacao_items : compensacao_items compensacao_item'''
    p[0] = p[1] + [p[2]]


def p_compensacao_items_single(p):
    '''compensacao_items : compensacao_item'''
    p[0] = [p[1]]


def p_compensacao_item_erro(p):
    '''compensacao_item : ERRO_START oracoes_opt ERRO_END'''
    p[0] = BlocoErro(corpo=p[2], lineno=p.lineno(1))


def p_compensacao_item_desempenho(p):
    '''compensacao_item : DESEMPENHO_START oracoes_opt DESEMPENHO_END'''
    p[0] = BlocoDesempenho(corpo=p[2], lineno=p.lineno(1))


def p_compensacao_item_alternativa(p):
    '''compensacao_item : ALTERNATIVA_START oracoes_opt ALTERNATIVA_END'''
    p[0] = BlocoAlternativa(corpo=p[2], lineno=p.lineno(1))


# ============================================================
# 4. ORAÇÕES DE CÓDIGO (Statements)
# ============================================================

# --- Oração simples (termina com ;) ---

def p_oracao_declaracao(p):
    '''oracao_de_codigo : declaracao_variavel SEMICOLON'''
    p[0] = p[1]


# --- Anotacao semantica (Buhler) como statement separado ---

def p_oracao_anotacao(p):
    '''oracao_de_codigo : SEMANTIC_ANNOTATION'''
    p[0] = AnotacaoSemantica(valor=p[1], lineno=p.lineno(1))


def p_oracao_definicao_funcao(p):
    '''oracao_de_codigo : definicao_funcao'''
    p[0] = p[1]


def p_oracao_definicao_classe(p):
    '''oracao_de_codigo : definicao_classe'''
    p[0] = p[1]


def p_oracao_atribuicao(p):
    '''oracao_de_codigo : atribuicao SEMICOLON'''
    p[0] = p[1]


def p_oracao_chamada_funcao(p):
    '''oracao_de_codigo : chamada_funcao SEMICOLON'''
    p[0] = p[1]


def p_oracao_chamada_metodo(p):
    '''oracao_de_codigo : chamada_metodo SEMICOLON'''
    p[0] = p[1]


def p_oracao_prop_atribuicao(p):
    '''oracao_de_codigo : prop_atribuicao SEMICOLON'''
    p[0] = p[1]


def p_oracao_retorno(p):
    '''oracao_de_codigo : RETURN_KEYWORD producao_de_valor SEMICOLON'''
    p[0] = Retorno(valor=p[2], lineno=p.lineno(1))


def p_oracao_retorno_vazio(p):
    '''oracao_de_codigo : RETURN_KEYWORD SEMICOLON'''
    p[0] = Retorno(valor=None, lineno=p.lineno(1))


def p_oracao_break(p):
    '''oracao_de_codigo : BREAK_KEYWORD SEMICOLON'''
    p[0] = Break(lineno=p.lineno(1))


def p_oracao_continue(p):
    '''oracao_de_codigo : CONTINUE_KEYWORD SEMICOLON'''
    p[0] = Continue(lineno=p.lineno(1))


# --- Orações compostas (não terminam com ;) ---

def p_oracao_if(p):
    '''oracao_de_codigo : if_statement'''
    p[0] = p[1]


def p_oracao_for(p):
    '''oracao_de_codigo : for_statement'''
    p[0] = p[1]


def p_oracao_while(p):
    '''oracao_de_codigo : while_statement'''
    p[0] = p[1]


def p_oracao_serie(p):
    '''oracao_de_codigo : serie_statement'''
    p[0] = p[1]


def p_oracao_paralelo(p):
    '''oracao_de_codigo : paralelo_statement'''
    p[0] = p[1]


def p_oracao_em(p):
    '''oracao_de_codigo : em_statement'''
    p[0] = p[1]


# ============================================================
# 5. DECLARAÇÕES E DEFINIÇÕES
# ============================================================

# --- Declaração de Variável ---

def p_declaracao_variavel_com_valor(p):
    '''declaracao_variavel : tipo ID ASSIGN producao_de_valor'''
    p[0] = DeclaracaoVariavel(tipo=p[1], nome=p[2], valor=p[4], lineno=p.lineno(1))


def p_declaracao_variavel_sem_valor(p):
    '''declaracao_variavel : tipo ID'''
    p[0] = DeclaracaoVariavel(tipo=p[1], nome=p[2], lineno=p.lineno(1))


def p_declaracao_com_caso(p):
    '''declaracao_variavel : caso_gramatical DOT tipo ID ASSIGN producao_de_valor'''
    p[0] = DeclaracaoVariavel(
        tipo=p[3], nome=p[4], valor=p[6],
        caso_gramatical=p[1], lineno=p.lineno(1)
    )


# --- Definição de Função ---




def p_definicao_funcao(p):
    '''definicao_funcao : caso_opt FUNCAO ID LPAREN parametros_opt RPAREN bloco_corpo'''
    p[0] = DefinicaoFuncao(
        nome=p[3], parametros=p[5],
        corpo=p[7], caso_gramatical=p[1],
        lineno=p.lineno(2)
    )


def p_definicao_funcao_com_retorno(p):
    '''definicao_funcao : caso_opt FUNCAO ID LPAREN parametros_opt RPAREN ARROW tipo bloco_corpo'''
    p[0] = DefinicaoFuncao(
        nome=p[3], parametros=p[5],
        tipo_retorno=p[8], corpo=p[9],
        caso_gramatical=p[1], lineno=p.lineno(2)
    )


def p_definicao_funcao_tipo_retorno(p):
    '''definicao_funcao : caso_opt tipo ID LPAREN parametros_opt RPAREN bloco_corpo'''
    p[0] = DefinicaoFuncao(
        nome=p[3], parametros=p[5],
        tipo_retorno=p[2], corpo=p[7],
        caso_gramatical=p[1], lineno=p.lineno(2)
    )


# --- Definição de Classe ---

def p_definicao_classe(p):
    '''definicao_classe : caso_opt CLASSE ID heranca_opt LBRACE membros_opt RBRACE'''
    extends = p[4][0] if p[4] else None
    implements = p[4][1] if p[4] else []
    p[0] = DefinicaoClasse(
        nome=p[3], superclasse=extends,
        interfaces=implements, membros=p[6],
        caso_gramatical=p[1], lineno=p.lineno(2)
    )


def p_heranca_opt_present(p):
    '''heranca_opt : EXTENDS ID implements_opt'''
    p[0] = (p[2], p[3])


def p_heranca_opt_implements_only(p):
    '''heranca_opt : implements_clause'''
    p[0] = (None, p[1])


def p_heranca_opt_empty(p):
    '''heranca_opt : empty'''
    p[0] = None


def p_implements_opt_present(p):
    '''implements_opt : implements_clause'''
    p[0] = p[1]


def p_implements_opt_empty(p):
    '''implements_opt : empty'''
    p[0] = []


def p_implements_clause(p):
    '''implements_clause : IMPLEMENTS id_list'''
    p[0] = p[2]


def p_id_list_multiple(p):
    '''id_list : id_list COMMA ID'''
    p[0] = p[1] + [p[3]]


def p_id_list_single(p):
    '''id_list : ID'''
    p[0] = [p[1]]


def p_membros_opt(p):
    '''membros_opt : oracoes'''
    p[0] = p[1]


def p_membros_opt_empty(p):
    '''membros_opt : empty'''
    p[0] = []


# ============================================================
# 6. HELPERS
# ============================================================

def p_caso_opt_present(p):
    '''caso_opt : caso_gramatical'''
    p[0] = p[1]


def p_caso_opt_empty(p):
    '''caso_opt : empty'''
    p[0] = None


def p_caso_gramatical(p):
    '''caso_gramatical : VOC
                       | NOM
                       | ACU
                       | DAT
                       | GEN
                       | INS
                       | LOC
                       | ABL'''
    p[0] = p[1]


def p_tipo(p):
    '''tipo : BOOL_TYPE
            | STRING_TYPE
            | INT_TYPE
            | FLOAT_TYPE
            | VOID_TYPE
            | FORMULA_TYPE
            | TEMPORAL_TYPE
            | IMAGEM_TYPE
            | AUDIO_TYPE
            | VIDEO_TYPE
            | ARRAY_TYPE
            | OBJECT_TYPE
            | TABELA_TYPE
            | GRAFO_TYPE
            | ID'''
    p[0] = p[1]


def p_tipo_array(p):
    '''tipo : tipo LBRACKET RBRACKET'''
    p[0] = f"{p[1]}[]"


def p_tipo_generico(p):
    '''tipo : tipo LESS_THAN tipo GREATER_THAN'''
    p[0] = f"{p[1]}<{p[3]}>"


def p_tipo_generico_duplo(p):
    '''tipo : tipo LESS_THAN tipo COMMA tipo GREATER_THAN'''
    p[0] = f"{p[1]}<{p[3]},{p[5]}>"


def p_parametros_opt_present(p):
    '''parametros_opt : parametros'''
    p[0] = p[1]


def p_parametros_opt_empty(p):
    '''parametros_opt : empty'''
    p[0] = []


def p_parametros_multiple(p):
    '''parametros : parametros COMMA parametro'''
    p[0] = p[1] + [p[3]]


def p_parametros_single(p):
    '''parametros : parametro'''
    p[0] = [p[1]]


def p_parametro(p):
    '''parametro : tipo ID'''
    p[0] = Parametro(tipo=p[1], nome=p[2], lineno=p.lineno(1))


def p_parametro_com_default(p):
    '''parametro : tipo ID ASSIGN producao_de_valor'''
    p[0] = Parametro(
        tipo=p[1], nome=p[2], valor_padrao=p[4],
        lineno=p.lineno(1)
    )


def p_bloco_corpo(p):
    '''bloco_corpo : LBRACE oracoes_opt RBRACE'''
    p[0] = p[2]


# ============================================================
# 7. CONTROLE DE FLUXO
# ============================================================



def p_if_elif_statement(p):
    '''if_statement : IF_KEYWORD LPAREN producao_de_valor RPAREN bloco_corpo elif_chain'''
    first = Se(condicao=p[3], corpo_verdadeiro=p[5], lineno=p.lineno(1))
    current = first
    # a producao tem 6 simbolos: p[6] e o elif_chain
    for cond, body in p[6]:
        node = Se(condicao=cond, corpo_verdadeiro=body, lineno=p.lineno(1))
        current.corpo_falso = [node]
        current = node
    p[0] = first



def p_elif_chain_multiple(p):
    '''elif_chain : elif_chain ELIF_KEYWORD LPAREN producao_de_valor RPAREN bloco_corpo'''
    p[0] = p[1] + [(p[4], p[6])]


def p_elif_chain_single(p):
    '''elif_chain : ELIF_KEYWORD LPAREN producao_de_valor RPAREN bloco_corpo'''
    p[0] = [(p[3], p[5])]


# --- Controle de Fluxo: se / senao_se / senao (if / elif / else) ---

def p_if_statement(p):
    '''if_statement : IF_KEYWORD LPAREN producao_de_valor RPAREN bloco_corpo else_opt'''
    p[0] = Se(condicao=p[3], corpo_verdadeiro=p[5], corpo_falso=p[6], lineno=p.lineno(1))


def p_else_opt_else(p):
    '''else_opt : ELSE_KEYWORD bloco_corpo'''
    p[0] = p[2]


def p_else_opt_elif(p):
    '''else_opt : ELIF_KEYWORD LPAREN producao_de_valor RPAREN bloco_corpo else_opt'''
    p[0] = Se(condicao=p[3], corpo_verdadeiro=p[5], corpo_falso=p[6], lineno=p.lineno(1))


def p_else_opt_empty(p):
    '''else_opt : empty'''
    p[0] = None


def p_for_statement(p):
    '''for_statement : FOR_KEYWORD LPAREN declaracao_variavel SEMICOLON producao_de_valor SEMICOLON atribuicao RPAREN bloco_corpo'''
    p[0] = Para(
        inicializacao=p[3], condicao=p[5],
        incremento=p[7], corpo=p[9], lineno=p.lineno(1)
    )


def p_for_each_statement(p):
    '''for_statement : FOR_KEYWORD LPAREN tipo ID COLON ID RPAREN bloco_corpo'''
    p[0] = ParaCada(
        tipo=p[3], variavel=p[4],
        iteravel=p[6], corpo=p[8], lineno=p.lineno(1)
    )


def p_while_statement(p):
    '''while_statement : WHILE_KEYWORD LPAREN producao_de_valor RPAREN bloco_corpo'''
    p[0] = Enquanto(condicao=p[3], corpo=p[5], lineno=p.lineno(1))


# ============================================================
# 8. EXECUÇÃO SÉRIE/PARALELO
# ============================================================

def p_serie_statement(p):
    '''serie_statement : SERIE_KEYWORD bloco_corpo'''
    p[0] = ExecucaoSerie(corpo=p[2], lineno=p.lineno(1))


def p_paralelo_statement(p):
    '''paralelo_statement : PARALELO_KEYWORD bloco_corpo'''
    p[0] = ExecucaoParalelo(corpo=p[2], lineno=p.lineno(1))


def p_em_statement(p):
    '''em_statement : EM_KEYWORD ID bloco_corpo'''
    p[0] = ExecucaoEm(linguagem=p[2], corpo=p[3], lineno=p.lineno(1))


# ============================================================
# 9. ATRIBUIÇÃO E CHAMADAS
# ============================================================

def p_atribuicao(p):
    '''atribuicao : ID ASSIGN producao_de_valor'''
    p[0] = Atribuicao(alvo=p[1], valor=p[3], lineno=p.lineno(1))


def p_atribuicao_com_caso(p):
    '''atribuicao : caso_gramatical DOT ID ASSIGN producao_de_valor'''
    p[0] = Atribuicao(
        alvo=p[3], valor=p[5],
        caso_gramatical=p[1], lineno=p.lineno(1)
    )


# --- Prop assignment: obj.prop = valor ---

def p_prop_atribuicao(p):
    '''prop_atribuicao : ID DOT ID ASSIGN producao_de_valor'''
    p[0] = PropAtribuicao(
        objeto=p[1], propriedade=p[3], valor=p[5],
        lineno=p.lineno(1)
    )


def p_prop_atribuicao_caso(p):
    '''prop_atribuicao : caso_gramatical DOT ID DOT ID ASSIGN producao_de_valor'''
    p[0] = PropAtribuicao(
        objeto=p[3], propriedade=p[5], valor=p[7],
        caso_gramatical=p[1], lineno=p.lineno(1)
    )


# --- Funcao / Metodo chamadas ---

def p_chamada_funcao(p):
    '''chamada_funcao : ID LPAREN argumentos_opt RPAREN'''
    p[0] = ChamadaFuncao(nome=p[1], argumentos=p[3], lineno=p.lineno(1))


def p_chamada_funcao_com_caso(p):
    '''chamada_funcao : caso_gramatical DOT ID LPAREN argumentos_opt RPAREN'''
    p[0] = ChamadaFuncao(
        nome=p[3], argumentos=p[5],
        caso_gramatical=p[1], lineno=p.lineno(1)
    )


def p_chamada_metodo(p):
    '''chamada_metodo : ID DOT ID LPAREN argumentos_opt RPAREN'''
    p[0] = ChamadaMetodo(
        objeto=p[1], metodo=p[3],
        argumentos=p[5], lineno=p.lineno(1)
    )


def p_chamada_metodo_com_caso(p):
    '''chamada_metodo : caso_gramatical DOT ID DOT ID LPAREN argumentos_opt RPAREN'''
    p[0] = ChamadaMetodo(
        objeto=p[3], metodo=p[5],
        argumentos=p[7], caso_gramatical=p[1],
        lineno=p.lineno(1)
    )


def p_argumentos_opt_present(p):
    '''argumentos_opt : argumentos'''
    p[0] = p[1]


def p_argumentos_opt_empty(p):
    '''argumentos_opt : empty'''
    p[0] = []


def p_argumentos_multiple(p):
    '''argumentos : argumentos COMMA producao_de_valor'''
    p[0] = p[1] + [p[3]]


def p_argumentos_single(p):
    '''argumentos : producao_de_valor'''
    p[0] = [p[1]]


# ============================================================
# 10. PRODUÇÕES DE VALOR (Expressions)
# ============================================================

# Operações binárias (precedência definida na tabela `precedence`)

def p_producao_binaria(p):
    '''producao_de_valor : producao_de_valor PLUS producao_de_valor
                         | producao_de_valor MINUS producao_de_valor
                         | producao_de_valor MULTIPLY producao_de_valor
                         | producao_de_valor DIVIDE producao_de_valor
                         | producao_de_valor MODULO producao_de_valor
                         | producao_de_valor EQUALS producao_de_valor
                         | producao_de_valor NOT_EQUALS producao_de_valor
                         | producao_de_valor LESS_THAN producao_de_valor
                         | producao_de_valor GREATER_THAN producao_de_valor
                         | producao_de_valor LESS_EQUAL producao_de_valor
                         | producao_de_valor GREATER_EQUAL producao_de_valor
                         | producao_de_valor AND producao_de_valor
                         | producao_de_valor OR producao_de_valor'''
    p[0] = OperacaoBinaria(
        esquerda=p[1], operador=p[2],
        direita=p[3], lineno=p.lineno(2)
    )


# Operações unárias

def p_producao_unaria_minus(p):
    '''producao_de_valor : MINUS producao_de_valor %prec UMINUS'''
    p[0] = OperacaoUnaria(operador='-', operando=p[2], lineno=p.lineno(1))


def p_producao_unaria_not(p):
    '''producao_de_valor : NOT producao_de_valor %prec UNOT'''
    p[0] = OperacaoUnaria(operador='!', operando=p[2], lineno=p.lineno(1))


# Agrupamento com parênteses

def p_producao_paren(p):
    '''producao_de_valor : LPAREN producao_de_valor RPAREN'''
    p[0] = p[2]


# Literais

def p_producao_string(p):
    '''producao_de_valor : STRING_LITERAL'''
    p[0] = Literal(valor=p[1], tipo='string', lineno=p.lineno(1))


def p_producao_int(p):
    '''producao_de_valor : INT_LITERAL'''
    p[0] = Literal(valor=p[1], tipo='int', lineno=p.lineno(1))


def p_producao_float(p):
    '''producao_de_valor : FLOAT_LITERAL'''
    p[0] = Literal(valor=p[1], tipo='float', lineno=p.lineno(1))


def p_producao_bool(p):
    '''producao_de_valor : BOOLEAN_LITERAL'''
    p[0] = Literal(valor=p[1], tipo='bool', lineno=p.lineno(1))


# Identificador

def p_producao_id(p):
    '''producao_de_valor : ID'''
    p[0] = Identificador(nome=p[1], lineno=p.lineno(1))


# Chamada de função como expressão

def p_producao_chamada_funcao(p):
    '''producao_de_valor : chamada_funcao'''
    p[0] = p[1]


def p_producao_chamada_metodo(p):
    '''producao_de_valor : chamada_metodo'''
    p[0] = p[1]


# Method call on string literal: "texto".metodo(args)

def p_producao_str_metodo(p):
    '''producao_de_valor : STRING_LITERAL DOT ID LPAREN argumentos_opt RPAREN'''
    lit = Literal(valor=p[1], tipo='string', lineno=p.lineno(1))
    p[0] = ChamadaMetodo(
        objeto=lit,
        metodo=p[3],
        argumentos=p[5],
        lineno=p.lineno(1)
    )


# Method call on array literal: [1,2,3].metodo(args)

def p_producao_arr_metodo(p):
    '''producao_de_valor : LBRACKET lista_valores_opt RBRACKET DOT ID LPAREN argumentos_opt RPAREN'''
    arr = ArrayLiteral(elementos=p[2] if p[2] else [], lineno=p.lineno(1))
    p[0] = ChamadaMetodo(
        objeto=arr,  # ArrayLiteral node directly
        metodo=p[6],
        argumentos=p[8],
        lineno=p.lineno(1)
    )


# Property access on string literal: "texto".prop

def p_producao_str_acesso(p):
    '''producao_de_valor : STRING_LITERAL DOT ID'''
    lit = Literal(valor=p[1], tipo='string', lineno=p.lineno(1))
    p[0] = AcessoPropriedade(
        objeto=lit,
        propriedade=p[3],
        lineno=p.lineno(1)
    )


# Acesso a propriedade

def p_producao_acesso(p):
    '''producao_de_valor : ID DOT ID'''
    p[0] = AcessoPropriedade(objeto=p[1], propriedade=p[3], lineno=p.lineno(1))


def p_producao_acesso_com_caso(p):
    '''producao_de_valor : caso_gramatical DOT ID DOT ID'''
    p[0] = AcessoPropriedade(
        objeto=p[3], propriedade=p[5],
        caso_gramatical=p[1], lineno=p.lineno(1)
    )


# Array literal

def p_producao_array_literal(p):
    '''producao_de_valor : LBRACKET lista_valores_opt RBRACKET'''
    p[0] = ArrayLiteral(elementos=p[2], lineno=p.lineno(1))


def p_lista_valores_opt_empty(p):
    '''lista_valores_opt : empty'''
    p[0] = []


def p_lista_valores_opt_present(p):
    '''lista_valores_opt : lista_valores'''
    p[0] = p[1]


def p_lista_valores_multiple(p):
    '''lista_valores : lista_valores COMMA producao_de_valor'''
    p[0] = p[1] + [p[3]]


def p_lista_valores_single(p):
    '''lista_valores : producao_de_valor'''
    p[0] = [p[1]]


# ============================================================
# 11. REGRA EMPTY E ERRO
# ============================================================

def p_empty(p):
    '''empty :'''
    p[0] = None


def p_error(p):
    if p:
        print(f"Erro sintático: token inesperado '{p.value}' (tipo: {p.type}) na linha {p.lineno}")
    else:
        print("Erro sintático: fim inesperado do arquivo")


# ============================================================
# 12. CONSTRUÇÃO E INTERFACE
# ============================================================

def build_parser(**kwargs):
    """Constrói e retorna o parser GuruDev®."""
    return yacc.yacc(start='programa', **kwargs)


def parse(source_code: str, debug: bool = False):
    """Faz parse de código GuruDev® e retorna a AST."""
    lexer = build_lexer()
    parser = build_parser(debug=debug)
    return parser.parse(source_code, lexer=lexer, debug=debug)


# ============================================================
# 13. TESTE
# ============================================================

if __name__ == '__main__':
    test_code = '''
[bloco]
    [sobrescrita]
        "Contexto: teste do parser"
        [nivel="literal"]
        [raiz="TEST"]
        [clave="ciencia"]
        [ont="acao"]
    [/sobrescrita]

    ¡codigo!
        NOM funcao somar(Int a, Int b) -> Int {
            return a + b;
        }

        String nome = "GuruDev";
        Int resultado = somar(10, 20);
    !/codigo!

    [subescritas]
        ¿python?
        def somar(a, b):
            return a + b
        ?/python?
    [/subescritas]
[/bloco]
'''

    ast = parse(test_code, debug=False)

    if ast:
        print("=" * 60)
        print("AST GERADA PELO GuruDev® Parser v1.0.0-alpha")
        print("=" * 60)
        print(ast)
    else:
        print("Falha no parsing.")
