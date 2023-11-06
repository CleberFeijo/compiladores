from ply import *


# palavras reservadas
reserved = {
    'function': 'FUNCTION',
    'procedure': 'PROCEDURE',
    'begin': 'BEGIN',
    'end': 'END',
    'const': 'CONST',
    'type': 'TYPE',
    'array': 'ARRAY',
    'of': 'OF',
    'record': 'RECORD',
    'var': 'VAR',
    'write': 'WRITE',
    'read': 'READ',
    'while': 'WHILE',
    'do': 'DO',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'return': 'RETURN',
    'not': 'NOT',
    'real': 'REAL_TYPE',
    'integer': 'INTEGER_TYPE'
}


tokens = [
    "STRING",
    "REAL_NUM",
    "INTEGER_NUM",
    "COLON",
    "SEMICOLON",
    "COMMA",
    "INITIALIZER",
    "ASSIGNMENT",
    "COMPARE",
    "NOTEQUAL",
    "LESSTHAN",
    "LESSTHANOREQUAL",
    "GREATERTHAN",
    "GREATERTHANOREQUAL",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "MODULO",
    "LEFTPARENTHESIS",
    "RIGHTPARENTHESIS",
    "LEFTBRACKET",
    "RIGHTBRACKET",
    "IDENTIFIER",
    "DOT",
    "COMMENT",
] + list(reserved.values())


# tokens e simbolos
# ( ) [ ] { } , ; + - * / == != > >= < <= || && ! = += -= *= /= %= ? :

t_STRING = r'("[^"\\]*(?:\\.[^"\\]*)*")'
t_IDENTIFIER = r"[a-zA-Z][a-zA-Z0-9]*"

t_LEFTPARENTHESIS = r"\("
t_RIGHTPARENTHESIS = r"\)"

t_LEFTBRACKET = r"\["
t_RIGHTBRACKET = r"\]"

t_COMMA = r','
t_DOT = r"\."
t_SEMICOLON = r';'
t_INITIALIZER = r"=="
t_ASSIGNMENT = r":="
t_COLON = r':'


t_COMPARE = r"="
t_NOTEQUAL = r"!="
t_LESSTHAN = r"<"
t_GREATERTHAN = r">"
t_LESSTHANOREQUAL = r"<="
t_GREATERTHANOREQUAL = r">="

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MODULO = r"%"


def generate_token_functions(reserved_dict):
    """
    Cria as funções para os campos do dict "reserved".
    """
    [
        exec(
            f"def t_{value}(t):\n" +
            f"\tr'{key}(?=(\s|;))'\n" +
            "\treturn t",
            globals()
        ) for key, value in reserved_dict.items()
    ]


# Chama a função para gerar as funções de tokenização
generate_token_functions(reserved)


def t_REAL_NUM(t):
    r'-?\d+(\.\d*([eE][-+]?\d+)?|[eE][-+]?\d+)'
    t.value = float(t.value)
    return t


def t_INTEGER_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# String contendo caracteres para serem ignorados
t_ignore = " \t\f"

# A string containing ignored characters (spaces and tabs)


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def t_COMMENT(t):
    r'\#[^\n]*'
    pass
    # No return value. Token discarded


lexer = lex.lex()
