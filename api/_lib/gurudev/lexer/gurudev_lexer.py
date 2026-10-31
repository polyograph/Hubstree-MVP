"""
GuruDev® Lexer — Versão 1.1.0-alpha
Analisador Léxico para a linguagem GuruDev®
Autor: Guilherme Gonçalves Machado
Ferramenta: PLY (Python Lex-Yacc)
"""

import sys
import ply.lex as lex
from typing import List, Optional

# Referência estável ao próprio módulo (necessária para PLY)
_this_module = sys.modules[__name__]

# ============================================================
# 1. LISTA DE TOKENS (OBRIGATÓRIA PARA PLY)
# ============================================================

tokens = (
    # Estruturas de blocos principais
    'BLOCO_START', 'BLOCO_END',
    'SOBRESCRITA_START', 'SOBRESCRITA_END',
    'SUBESCRITAS_START', 'SUBESCRITAS_END',
    'CODIGO_START', 'CODIGO_END',

    # Blocos de interoperabilidade avançada
    'COMPENSACAO_START', 'COMPENSACAO_END',
    'ERRO_START', 'ERRO_END',
    'DESEMPENHO_START', 'DESEMPENHO_END',
    'ALTERNATIVA_START', 'ALTERNATIVA_END',

    # Subescritas de linguagens estrangeiras
    'PYTHON_START', 'PYTHON_END',
    'RUST_START', 'RUST_END',
    'JAVASCRIPT_START', 'JAVASCRIPT_END',
    'CSHARP_START', 'CSHARP_END',
    'WASM_START', 'WASM_END',
    'CPP_START', 'CPP_END',
    'JAVA_START', 'JAVA_END',
    'SQL_START', 'SQL_END',
    'R_START', 'R_END',

    # Conteúdo bruto de código estrangeiro
    'FOREIGN_CODE_CONTENT',

    # Atributos de sobrescrita
    'NIVEL_ATTR', 'RAIZ_ATTR', 'CLAVE_ATTR', 'ONT_ATTR',
    # Niveis Hermeneuticos - Canonicos (1-7) + Estendidos (8-13)
    'NIVEL_LITERAL', 'NIVEL_ALEGORICO', 'NIVEL_MORAL', 'NIVEL_MISTICO',
    'NIVEL_FUNCIONAL', 'NIVEL_ESTETICO', 'NIVEL_ONTOLOGICO',
    'NIVEL_HOLISTICO', 'NIVEL_MATEMATICO', 'NIVEL_SIMBOLICO',
    'NIVEL_PARABOLICO', 'NIVEL_HISTORICO', 'NIVEL_LINGUISTICO',
    'CLAVE_ARTE', 'CLAVE_CIENCIA', 'CLAVE_FILOSOFIA', 'CLAVE_GERAL',
    'ONT_ACAO',
    'PARADIGMA_ATTR', 'PARADIGMA_IMPERATIVO', 'PARADIGMA_FUNCIONAL', 'PARADIGMA_OO',
    'PARADIGMA_LOGICO', 'PARADIGMA_DECLARATIVO', 'PARADIGMA_VQE', 'PARADIGMA_QAOA',
    'PARADIGMA_QUANTICO', 'PARADIGMA_QUANTUM', 'PARADIGMA_VARIACIONAL', 'PARADIGMA_HIBRIDO',

    # Casos gramaticais
    'VOC', 'NOM', 'ACU', 'DAT', 'GEN', 'INS', 'LOC', 'ABL',

    # Palavras-chave estruturais
    'FUNCAO', 'CLASSE', 'EXTENDS', 'IMPLEMENTS',

    # Tipos de dados
    'BOOL_TYPE', 'STRING_TYPE', 'INT_TYPE', 'FLOAT_TYPE', 'VOID_TYPE',
    'ARRAY_TYPE', 'OBJECT_TYPE', 'FORMULA_TYPE', 'TEMPORAL_TYPE',
    'IMAGEM_TYPE', 'AUDIO_TYPE', 'VIDEO_TYPE', 'TABELA_TYPE', 'GRAFO_TYPE',

    # Controle de fluxo
    'IF_KEYWORD', 'ELSE_KEYWORD', 'FOR_KEYWORD', 'WHILE_KEYWORD',
    'RETURN_KEYWORD', 'BREAK_KEYWORD', 'CONTINUE_KEYWORD', 'ELIF_KEYWORD',
    'SEMANTIC_ANNOTATION',

    # Execução série/paralelo
    'SERIE_KEYWORD', 'PARALELO_KEYWORD', 'EM_KEYWORD',

    # Literais
    'STRING_LITERAL', 'INT_LITERAL', 'FLOAT_LITERAL', 'BOOLEAN_LITERAL',

    # Identificador
    'ID',

    # Operadores (multi-caractere primeiro)
    'EQUALS', 'NOT_EQUALS', 'LESS_EQUAL', 'GREATER_EQUAL',
    'AND', 'OR', 'ARROW',
    'ASSIGN', 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MODULO',
    'LESS_THAN', 'GREATER_THAN', 'NOT',

    # Delimitadores
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET',
    'SEMICOLON', 'COMMA', 'DOT', 'COLON',
)

# ============================================================
# 2. ESTADOS DO LEXER
# ============================================================

states = (
    ('sobrescrita', 'exclusive'),
    ('gurudevcode', 'exclusive'),
    ('compensacao', 'exclusive'),
    ('pycode', 'exclusive'),
    ('rustcode', 'exclusive'),
    ('jscode', 'exclusive'),
    ('csharpcode', 'exclusive'),
    ('wasmcode', 'exclusive'),
    ('cppcode', 'exclusive'),
    ('javacode', 'exclusive'),
    ('sqlcode', 'exclusive'),
    ('rcode', 'exclusive'),
)

# ============================================================
# 3. PALAVRAS RESERVADAS
# ============================================================

reserved = {
    # Casos gramaticais (MAIÚSCULAS)
    'VOC': 'VOC', 'NOM': 'NOM', 'ACU': 'ACU', 'DAT': 'DAT',
    'GEN': 'GEN', 'INS': 'INS', 'LOC': 'LOC', 'ABL': 'ABL',
    
    # Estruturais
    'funcao': 'FUNCAO', 'classe': 'CLASSE',
    'extends': 'EXTENDS', 'implements': 'IMPLEMENTS',
    
    # Controle de fluxo (com aliases em português)
    'if': 'IF_KEYWORD', 'se': 'IF_KEYWORD',
    'else': 'ELSE_KEYWORD', 'senao': 'ELSE_KEYWORD',
    'elif': 'ELIF_KEYWORD', 'senao_se': 'ELIF_KEYWORD',
    'for': 'FOR_KEYWORD', 'para': 'FOR_KEYWORD',
    'while': 'WHILE_KEYWORD', 'enquanto': 'WHILE_KEYWORD',
    'return': 'RETURN_KEYWORD', 'retorna': 'RETURN_KEYWORD',
    'break': 'BREAK_KEYWORD', 'quebra': 'BREAK_KEYWORD',
    'continue': 'CONTINUE_KEYWORD', 'continua': 'CONTINUE_KEYWORD',
    
    # Execução
    'serie': 'SERIE_KEYWORD', 'paralelo': 'PARALELO_KEYWORD', 'em': 'EM_KEYWORD',
    
    # Tipos de dados (PascalCase)
    'Bool': 'BOOL_TYPE', 'String': 'STRING_TYPE', 'Int': 'INT_TYPE',
    'Float': 'FLOAT_TYPE', 'Void': 'VOID_TYPE', 'Array': 'ARRAY_TYPE',
    'Object': 'OBJECT_TYPE', 'Formula': 'FORMULA_TYPE', 'Temporal': 'TEMPORAL_TYPE',
    'Imagem': 'IMAGEM_TYPE', 'Audio': 'AUDIO_TYPE', 'Video': 'VIDEO_TYPE',
    'Tabela': 'TABELA_TYPE', 'Grafo': 'GRAFO_TYPE',
    
    # Booleanos
    'true': 'BOOLEAN_LITERAL', 'false': 'BOOLEAN_LITERAL',
    'verdadeiro': 'BOOLEAN_LITERAL', 'falso': 'BOOLEAN_LITERAL',
}

# ============================================================
# 4. MAPAS SEMÂNTICOS
# ============================================================

# Niveis Hermeneuticos
# ------------------
# Canonicos (1-7): definidos no WHITEPAPER §4, GURU_MATRIX5D e GURUBYTE
#   1=Literal  2=Alegorico  3=Moral  4=Mistico  5=Funcional  6=Estetico  7=Ontologico
# Estendidos (8-13): niveis auxiliares para dominios especificos
#   8=Holistico  9=Matematico  10=Simbolico  11=Parabolico  12=Historico  13=Linguistico
#
nivel_map = {
    # --- Canonicos (1-7) ---
    'literal':    'NIVEL_LITERAL',
    'alegorico':  'NIVEL_ALEGORICO',
    'moral':      'NIVEL_MORAL',
    'mistico':    'NIVEL_MISTICO',
    'funcional':  'NIVEL_FUNCIONAL',
    'estetico':   'NIVEL_ESTETICO',
    'ontologico': 'NIVEL_ONTOLOGICO',
    # --- Estendidos (8-13) ---
    'holistico':   'NIVEL_HOLISTICO',
    'matematico':  'NIVEL_MATEMATICO',
    'simbolico':   'NIVEL_SIMBOLICO',
    'parabolico':  'NIVEL_PARABOLICO',
    'historico':   'NIVEL_HISTORICO',
    'linguistico': 'NIVEL_LINGUISTICO',
}

clave_map = {
    'arte': 'CLAVE_ARTE',
    'ciencia': 'CLAVE_CIENCIA',
    'filosofia': 'CLAVE_FILOSOFIA',
    'geral': 'CLAVE_GERAL',
}

ont_map = {
    'acao': 'ONT_ACAO',
}


paradigma_map = {
    'imperativo': 'PARADIGMA_IMPERATIVO',
    'funcional': 'PARADIGMA_FUNCIONAL',
    'orientado_a_objetos': 'PARADIGMA_OO',
    'logico': 'PARADIGMA_LOGICO',
    'declarativo': 'PARADIGMA_DECLARATIVO',
    'vqe': 'PARADIGMA_VQE',
    'qaoa': 'PARADIGMA_QAOA',
    'quantico': 'PARADIGMA_QUANTICO',
    'quantum': 'PARADIGMA_QUANTUM',
    'variacional': 'PARADIGMA_VARIACIONAL',
    'hibrido': 'PARADIGMA_HIBRIDO',
}


# ============================================================
# 5. CARACTERES IGNORADOS
# ============================================================

t_ignore = ' \t'
t_sobrescrita_ignore = ' \t'
t_gurudevcode_ignore = ' \t'
t_compensacao_ignore = ' \t'

# ============================================================
# 6. REGRAS DO ESTADO INITIAL
# ============================================================

# --- Transições de Estado ---

def t_SOBRESCRITA_START(t):
    r'\[sobrescrita\]|\[?\$\$sobrescrita\$\$\]?'
    t.lexer.push_state('sobrescrita')
    return t

def t_CODIGO_START(t):
    r'¡codigo!'
    t.lexer.push_state('gurudevcode')
    return t

def t_COMPENSACAO_START(t):
    r'\[compensacao\]|\$\$compensacao\$\$'
    t.lexer.push_state('compensacao')
    return t

# --- Tags que não mudam de estado ---
def t_BLOCO_START(t):
    r'\[bloco\]|\[?\$\$bloco\$\$\]?'
    return t

def t_BLOCO_END(t):
    r'\[/bloco\]|\[?\$\$/bloco\$\$\]?'
    return t

def t_SUBESCRITAS_START(t):
    r'\[subescritas\]|\[?\$\$subescritas\$\$\]?'
    return t

def t_SUBESCRITAS_END(t):
    r'\[/subescritas\]|\[?\$\$/subescritas\$\$\]?'
    return t

# --- Início de linguagens estrangeiras ---

def t_PYTHON_START(t):
    r'¿python\?'
    t.lexer.push_state('pycode')
    return t

def t_RUST_START(t):
    r'¿rust\?'
    t.lexer.push_state('rustcode')
    return t

def t_JAVASCRIPT_START(t):
    r'¿javascript\?'
    t.lexer.push_state('jscode')
    return t

def t_CSHARP_START(t):
    r'¿csharp\?'
    t.lexer.push_state('csharpcode')
    return t

def t_WASM_START(t):
    r'¿wasm\?'
    t.lexer.push_state('wasmcode')
    return t

def t_CPP_START(t):
    r'¿c\+\+\?'
    t.lexer.push_state('cppcode')
    return t

def t_JAVA_START(t):
    r'¿java\?'
    t.lexer.push_state('javacode')
    return t

def t_SQL_START(t):
    r'¿sql\?'
    t.lexer.push_state('sqlcode')
    return t

def t_R_START(t):
    r'¿r\?'
    t.lexer.push_state('rcode')
    return t

# --- Comentários (INITIAL) ---

def t_COMMENT_MULTI(t):
    r'/\*[\s\S]*?\*/'
    t.lexer.lineno += t.value.count('\n')

def t_COMMENT_SINGLE(t):
    r'//[^\n]*'
    pass

# --- Newline ---

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# --- Literais (INITIAL — para top-level statements) ---

def t_STRING_LITERAL(t):
    r'"([^"\\]|\\.)*"'
    t.value = t.value[1:-1]
    return t

def t_FLOAT_LITERAL(t):
    r'\d+\.\d+f?'
    t.value = float(t.value.replace('f', ''))
    return t

def t_INT_LITERAL(t):
    r'\d+'
    t.value = int(t.value)
    return t

# --- Operadores multi-caractere (funções para prioridade) ---

def t_EQUALS(t):
    r'=='
    return t

def t_NOT_EQUALS(t):
    r'!='
    return t

def t_LESS_EQUAL(t):
    r'<='
    return t

def t_GREATER_EQUAL(t):
    r'>='
    return t

def t_AND(t):
    r'&&'
    return t

def t_OR(t):
    r'\|\|'
    return t

def t_ARROW(t):
    r'->'
    return t

# --- Operadores uni-caractere ---
t_ASSIGN = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_MODULO = r'%'
t_LESS_THAN = r'<'
t_GREATER_THAN = r'>'
t_NOT = r'!'

# --- Delimitadores ---
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMICOLON = r';'
t_COMMA = r','
t_DOT = r'\.'
t_COLON = r':'


# Semantic annotation: #sem: puro / #sem: efeito / #sem: expressao
def t_SEMANTIC_ANNOTATION(t):
    r'\#sem:\s*\w+'
    # Extract value after #sem:
    t.value = t.value.split(':')[1].strip()
    return t

# --- Identificadores e Palavras Reservadas ---

def t_ID(t):
    r'[a-zA-ZÀ-ÿ_][a-zA-ZÀ-ÿ0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    if t.type == 'BOOLEAN_LITERAL':
        t.value = t.value.lower() in ('true', 'verdadeiro', '1')
    return t

# --- Erro ---

def t_error(t):
    print(f"[INITIAL] Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

# ============================================================
# 7. REGRAS DO ESTADO SOBRESCRITA
# ============================================================

def t_sobrescrita_NIVEL_ATTR(t):
    r'\[nivel="([^"]+)"\]|\[?\$\$nivel="([^"]+)"\$\$\]?'
    # Strip optional brackets from match
    if t.value.startswith('[') and t.value.endswith(']'):
        t.value = t.value[1:-1]
    val = t.value[t.value.find('"')+1:t.value.rfind('"')].lower()
    t.type = nivel_map.get(val, 'NIVEL_ATTR')
    t.value = val
    return t

def t_sobrescrita_RAIZ_ATTR(t):
    r'\[raiz="([^"]+)"\]|\[?\$\$raiz="([^"]+)"\$\$\]?'
    if t.value.startswith('[') and t.value.endswith(']'):
        t.value = t.value[1:-1]
    t.value = t.value[t.value.find('"')+1:t.value.rfind('"')]
    return t

def t_sobrescrita_CLAVE_ATTR(t):
    r'\[clave="([^"]+)"\]|\[?\$\$clave="([^"]+)"\$\$\]?'
    if t.value.startswith('[') and t.value.endswith(']'):
        t.value = t.value[1:-1]
    val = t.value[t.value.find('"')+1:t.value.rfind('"')].lower()
    t.type = clave_map.get(val, 'CLAVE_ATTR')
    t.value = val
    return t

def t_sobrescrita_ONT_ATTR(t):
    r'\[ont="([^"]+)"\]|\[?\$\$ont="([^"]+)"\$\$\]?'
    if t.value.startswith('[') and t.value.endswith(']'):
        t.value = t.value[1:-1]
    val = t.value[t.value.find('"')+1:t.value.rfind('"')].lower()
    t.type = ont_map.get(val, 'ONT_ATTR')
    t.value = val
    return t



def t_sobrescrita_PARADIGMA_ATTR(t):
    r'\[?\$\$paradigma="([^"]+)"\$\$\]?'
    if t.value.startswith('[') and t.value.endswith(']'):
        t.value = t.value[1:-1]
    val = t.value[t.value.find('"')+1:t.value.rfind('"')].lower()
    t.type = paradigma_map.get(val, 'PARADIGMA_ATTR')
    t.value = val
    return t
def t_sobrescrita_STRING_LITERAL(t):
    r'"([^"\\]|\\.)*"'
    t.value = t.value[1:-1]
    return t


def t_sobrescrita_GENERIC_ATTR(t):
    r'\[?\$?\$?[a-zA-Z\xc0-\xff_][a-zA-Z\xc0-\xff0-9_]*="([^"]+)"\$?\$?\]?'
    keyword = t.value.split('=')[0].split('$')[-1].split('[')[-1].strip()
    if keyword in ('nivel', 'raiz', 'clave', 'ont'):
        t.lexer.skip(len(t.value))
        return
    val = t.value[t.value.find('"')+1:t.value.rfind('"')]
    t.type = 'STRING_LITERAL'
    t.value = val
    return t

def t_sobrescrita_SOBRESCRITA_END(t):
    r'\[/sobrescrita\]|\[?\$\$/sobrescrita\$\$\]?'
    t.lexer.pop_state()
    return t

def t_sobrescrita_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_sobrescrita_error(t):
    print(f"[SOBRESCRITA] Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

# ============================================================
# 8. REGRAS DO ESTADO GURUDEVCODE
# ============================================================

# Comentários
def t_gurudevcode_COMMENT_MULTI(t):
    r'/\*[\s\S]*?\*/'
    t.lexer.lineno += t.value.count('\n')

def t_gurudevcode_COMMENT_SINGLE(t):
    r'//[^\n]*'
    pass

# Newline
def t_gurudevcode_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Literais
def t_gurudevcode_STRING_LITERAL(t):
    r'"([^"\\]|\\.)*"'
    t.value = t.value[1:-1]
    return t

def t_gurudevcode_FLOAT_LITERAL(t):
    r'\d+\.\d+f?'
    t.value = float(t.value.replace('f', ''))
    return t

def t_gurudevcode_INT_LITERAL(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Operadores multi-caractere (funções)
def t_gurudevcode_EQUALS(t):
    r'=='
    return t
def t_gurudevcode_NOT_EQUALS(t):
    r'!='
    return t
def t_gurudevcode_LESS_EQUAL(t):
    r'<='
    return t
def t_gurudevcode_GREATER_EQUAL(t):
    r'>='
    return t
def t_gurudevcode_AND(t):
    r'&&'
    return t
def t_gurudevcode_OR(t):
    r'\|\|'
    return t
def t_gurudevcode_ARROW(t):
    r'->'
    return t

# Operadores uni-caractere
t_gurudevcode_ASSIGN = r'='
t_gurudevcode_PLUS = r'\+'
t_gurudevcode_MINUS = r'-'
t_gurudevcode_MULTIPLY = r'\*'
t_gurudevcode_DIVIDE = r'/'
t_gurudevcode_MODULO = r'%'
t_gurudevcode_LESS_THAN = r'<'
t_gurudevcode_GREATER_THAN = r'>'
t_gurudevcode_NOT = r'!'

# Delimitadores
t_gurudevcode_LPAREN = r'\('
t_gurudevcode_RPAREN = r'\)'
t_gurudevcode_LBRACE = r'\{'
t_gurudevcode_RBRACE = r'\}'
t_gurudevcode_LBRACKET = r'\['
t_gurudevcode_RBRACKET = r'\]'
t_gurudevcode_SEMICOLON = r';'
t_gurudevcode_COMMA = r','
t_gurudevcode_DOT = r'\.'
t_gurudevcode_COLON = r':'

# Identificadores e Palavras Reservadas


def t_gurudevcode_SEMANTIC_ANNOTATION(t):
    r'\#sem:\s*\w+'
    t.value = t.value.split(':')[1].strip()
    return t

def t_gurudevcode_ID(t):
    r'[a-zA-ZÀ-ÿ_][a-zA-ZÀ-ÿ0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    if t.type == 'BOOLEAN_LITERAL':
        t.value = t.value.lower() in ('true', 'verdadeiro', '1')
    return t

# Fim do bloco de código GuruDev®
def t_gurudevcode_CODIGO_END(t):
    r'[!\xa1]/codigo!'
    t.lexer.pop_state()
    return t


def t_gurudevcode_BLOCO_START(t):
    r'\$\$bloco\$\$'
    return t
def t_gurudevcode_BLOCO_END(t):
    r'\$\$/bloco\$\$'
    return t
def t_gurudevcode_SOBRESCRITA_START(t):
    r'\$\$sobrescrita\$\$'
    t.lexer.push_state('sobrescrita')
    return t
def t_gurudevcode_SOBRESCRITA_END(t):
    r'\$\$/sobrescrita\$\$'
    t.lexer.pop_state()
    return t
def t_gurudevcode_SUBESCRITAS_START(t):
    r'\$\$subescritas\$\$'
    return t
def t_gurudevcode_SUBESCRITAS_END(t):
    r'\$\$/subescritas\$\$'
    return t

def t_gurudevcode_error(t):
    print(f"[GURUDEVCODE] Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

# ============================================================

# ============================================================
# 9. STATIC FOREIGN LANGUAGE RULES
# ============================================================

t_pycode_ignore = ' \t'
def t_pycode_FOREIGN_CODE_CONTENT(t):
    r'[\s\S]+?(?=\?/python\?)'
    t.type = 'FOREIGN_CODE_CONTENT'
    t.lexer.lineno += t.value.count('\n')
    return t
def t_pycode_PYTHON_END(t):
    r'\?/python\?'
    t.lexer.pop_state()
    return t
def t_pycode_error(t):
    t.lexer.skip(1)

t_rustcode_ignore = ' \t'
def t_rustcode_FOREIGN_CODE_CONTENT(t):
    r'[\s\S]+?(?=\?/rust\?)'
    t.type = 'FOREIGN_CODE_CONTENT'
    t.lexer.lineno += t.value.count('\n')
    return t
def t_rustcode_RUST_END(t):
    r'\?/rust\?'
    t.lexer.pop_state()
    return t
def t_rustcode_error(t):
    t.lexer.skip(1)

t_jscode_ignore = ' \t'
def t_jscode_FOREIGN_CODE_CONTENT(t):
    r'[\s\S]+?(?=\?/javascript\?)'
    t.type = 'FOREIGN_CODE_CONTENT'
    t.lexer.lineno += t.value.count('\n')
    return t
def t_jscode_JAVASCRIPT_END(t):
    r'\?/javascript\?'
    t.lexer.pop_state()
    return t
def t_jscode_error(t):
    t.lexer.skip(1)

t_csharpcode_ignore = ' \t'
def t_csharpcode_FOREIGN_CODE_CONTENT(t):
    r'[\s\S]+?(?=\?/csharp\?)'
    t.type = 'FOREIGN_CODE_CONTENT'
    t.lexer.lineno += t.value.count('\n')
    return t
def t_csharpcode_CSHARP_END(t):
    r'\?/csharp\?'
    t.lexer.pop_state()
    return t
def t_csharpcode_error(t):
    t.lexer.skip(1)

t_wasmcode_ignore = ' \t'
def t_wasmcode_FOREIGN_CODE_CONTENT(t):
    r'[\s\S]+?(?=\?/wasm\?)'
    t.type = 'FOREIGN_CODE_CONTENT'
    t.lexer.lineno += t.value.count('\n')
    return t
def t_wasmcode_WASM_END(t):
    r'\?/wasm\?'
    t.lexer.pop_state()
    return t
def t_wasmcode_error(t):
    t.lexer.skip(1)

t_cppcode_ignore = ' \t'
def t_cppcode_FOREIGN_CODE_CONTENT(t):
    r'[\s\S]+?(?=\?/c\+\+\?)'
    t.type = 'FOREIGN_CODE_CONTENT'
    t.lexer.lineno += t.value.count('\n')
    return t
def t_cppcode_CPP_END(t):
    r'\?/c\+\+\?'
    t.lexer.pop_state()
    return t
def t_cppcode_error(t):
    t.lexer.skip(1)

t_javacode_ignore = ' \t'
def t_javacode_FOREIGN_CODE_CONTENT(t):
    r'[\s\S]+?(?=\?/java\?)'
    t.type = 'FOREIGN_CODE_CONTENT'
    t.lexer.lineno += t.value.count('\n')
    return t
def t_javacode_JAVA_END(t):
    r'\?/java\?'
    t.lexer.pop_state()
    return t
def t_javacode_error(t):
    t.lexer.skip(1)

t_sqlcode_ignore = ' \t'
def t_sqlcode_FOREIGN_CODE_CONTENT(t):
    r'[\s\S]+?(?=\?/sql\?)'
    t.type = 'FOREIGN_CODE_CONTENT'
    t.lexer.lineno += t.value.count('\n')
    return t
def t_sqlcode_SQL_END(t):
    r'\?/sql\?'
    t.lexer.pop_state()
    return t
def t_sqlcode_error(t):
    t.lexer.skip(1)

t_rcode_ignore = ' \t'
def t_rcode_FOREIGN_CODE_CONTENT(t):
    r'[\s\S]+?(?=\?/r\?)'
    t.type = 'FOREIGN_CODE_CONTENT'
    t.lexer.lineno += t.value.count('\n')
    return t
def t_rcode_R_END(t):
    r'\?/r\?'
    t.lexer.pop_state()
    return t
def t_rcode_error(t):
    t.lexer.skip(1)

# 10. REGRAS PARA COMPENSAÇÃO, PLÁSTICO, MODULAÇÃO
# ============================================================

# Estado compensacao — herda regras do gurudevcode + sub-blocos

def t_compensacao_ERRO_START(t):
    r'\$\$erro[^\$\$]*\]'
    return t

def t_compensacao_ERRO_END(t):
    r'\$\$/erro\$\$'
    return t

def t_compensacao_DESEMPENHO_START(t):
    r'\$\$desempenho[^\$\$]*\]'
    return t

def t_compensacao_DESEMPENHO_END(t):
    r'\$\$/desempenho\$\$'
    return t

def t_compensacao_ALTERNATIVA_START(t):
    r'\$\$alternativa[^\$\$]*\]'
    return t

def t_compensacao_ALTERNATIVA_END(t):
    r'\$\$/alternativa\$\$'
    return t

def t_compensacao_COMPENSACAO_END(t):
    r'\[/compensacao\]|\$\$/compensacao\$\$'
    t.lexer.pop_state()
    return t

# Reutilizar regras do gurudevcode para o conteúdo de compensação
t_compensacao_SEMICOLON = t_gurudevcode_SEMICOLON
t_compensacao_LPAREN = t_gurudevcode_LPAREN
t_compensacao_RPAREN = t_gurudevcode_RPAREN
t_compensacao_LBRACE = t_gurudevcode_LBRACE
t_compensacao_RBRACE = t_gurudevcode_RBRACE
t_compensacao_DOT = t_gurudevcode_DOT
t_compensacao_COMMA = t_gurudevcode_COMMA
t_compensacao_COLON = t_gurudevcode_COLON
t_compensacao_ASSIGN = t_gurudevcode_ASSIGN
t_compensacao_PLUS = t_gurudevcode_PLUS
t_compensacao_MINUS = t_gurudevcode_MINUS
t_compensacao_MULTIPLY = t_gurudevcode_MULTIPLY
t_compensacao_DIVIDE = t_gurudevcode_DIVIDE

def t_compensacao_STRING_LITERAL(t):
    r'"([^"\\]|\\.)*"'
    t.value = t.value[1:-1]
    return t

def t_compensacao_FLOAT_LITERAL(t):
    r'\d+\.\d+f?'
    t.value = float(t.value.replace('f', ''))
    return t

def t_compensacao_INT_LITERAL(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_compensacao_ID(t):
    r'[a-zA-ZÀ-ÿ_][a-zA-ZÀ-ÿ0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    if t.type == 'BOOLEAN_LITERAL':
        t.value = t.value.lower() in ('true', 'verdadeiro', '1')
    return t

def t_compensacao_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_compensacao_COMMENT_SINGLE(t):
    r'//[^\n]*'
    pass

def t_compensacao_error(t):
    print(f"[COMPENSACAO] Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

# Estados plastico e modulacao teriam regras similares
# (omitidos por brevidade, mas seguem o mesmo padrão)

# ============================================================
# 11. CONSTRUÇÃO E INTERFACE
# ============================================================

def build_lexer(**kwargs):
    """Constrói e retorna o lexer GuruDev®."""
    return lex.lex(module=_this_module, **kwargs)

def tokenize(source_code: str) -> List:
    """Tokeniza código-fonte GuruDev® e retorna lista de tokens."""
    lexer = build_lexer()
    lexer.input(source_code)
    result = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        result.append(tok)
    return result

# ============================================================
# 12. TESTE
# ============================================================

if __name__ == '__main__':
    test_code = '''
[bloco]
    [sobrescrita]
        "Contexto: autenticação de usuário"
        [nivel="holistico"]
        [raiz="SEG"]
        [clave="ciencia"]
        [ont="acao"]
    [/sobrescrita]

    ¡codigo!
        NOM funcao verificarSenha(String senhaInserida, String senhaHash) {
            return hash(senhaInserida) == hash(senhaHash);
        }

        serie {
            em python { dados = processar("data.csv") }
            em rust { resultado = validar(dados) }
        }
    !/codigo!

    [subescritas]
        ¿python?
        def verificar_senha(senha_inserida, senha_armazenada):
            return hash(senha_inserida) == hash(senha_armazenada)
        ?/python?

        ¿rust?
        fn verificar_senha(s1: &str, s2: &str) -> bool {
            hash(s1) == hash(s2)
        }
        ?/rust?
    [/subescritas]
[/bloco]

// Top-level statement
String nome = "Guilherme";
VOC.console.log(nome);
'''

    tokens_result = tokenize(test_code)
    
    print("=" * 60)
    print("TOKENS GERADOS PELO GuruDev® Lexer v1.1.0-alpha")
    print("=" * 60)
    
    for tok in tokens_result:
        print(f"  {tok.type:30s} | {str(tok.value):40s} | linha {tok.lineno}")
    
    print(f"\nTotal: {len(tokens_result)} tokens")
