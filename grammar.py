#!/usr/bin/python
import pprint

import ply.yacc as yacc

import errors
from declaration import *
from lex import tokens

log_erros = {}

transcription = open("transcricao.txt", "w")


def lista_continua(lista):
    min_valor = min(lista)
    max_valor = max(lista)

    esperado = set(range(min_valor, max_valor + 1))

    return set(lista) == esperado


# Parsing rules
precedence = (
    ('left', 'LEFTPARENTHESIS', 'RIGHTPARENTHESIS'),
    ('left', 'GREATERTHAN', 'LESSTHAN', 'GREATERTHANOREQUAL', 'LESSTHANOREQUAL',
     'COMPARE', 'NOTEQUAL'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'NOT'),
)


# ------------------------------------------------------------------------------

def p_empty(p):
    'empty :'
    pass


def p_programa(t):
    '''
    PROGRAMA : DECLARACOES BLOCO
    '''
    t[0] = (t[1], t[2])
    pp = pprint.PrettyPrinter(width=30, compact=True)
    formatted_data = pp.pformat(t[0])
    transcription.write(formatted_data)


def p_declaracoes(t):
    '''
    DECLARACOES : DEF_CONST DEF_TIPOS DEF_VAR DEF_ROT
    '''
    if len(t) == 2:
        t[0] = [t[1]]  # Se for uma única declaração, armazene-a em uma lista
    else:
        t[0] = [t[1]] + [t[2]] + [t[3]] + [t[4]]


def p_def_const(t):
    '''
    DEF_CONST : CONST CONSTANTE SEMICOLON LIST_CONST
              | empty
    '''
    if len(t) > 2:
        t[0] = ('DEF_CONST', [t[2], *t[4]])
    else:
        t[0] = None


def p_list_const(t):
    '''
    LIST_CONST : CONSTANTE SEMICOLON LIST_CONST
               | empty
    '''
    if len(t) == 4:
        t[0] = (t[1], *t[3])
    else:
        t[0] = ()


def p_constante(t):
    '''
    CONSTANTE : ID INITIALIZER CONST_VALOR
    '''
    t[0] = ('CONSTANTE', t[1], t[3])


def p_const_valor(t):
    '''
    CONST_VALOR : STRING
                | EXP_MAT
    '''
    t[0] = ('CONST_VALOR', t[1])


def p_def_tipos(t):
    '''
    DEF_TIPOS : TYPE TIPO SEMICOLON LIST_TIPOS
              | empty
    '''
    if len(t) > 2:
        t[0] = ('DEF_TIPOS', [t[2], t[4]])
    else:
        t[0] = []


def p_list_tipos(t):
    '''
    LIST_TIPOS : TIPO SEMICOLON LIST_TIPOS
               | empty
    '''
    if len(t) > 2:
        t[0] = t[1] + t[3]
    else:
        t[0] = ()


def p_tipo(t):
    '''
    TIPO : ID INITIALIZER TIPO_DADO
    '''
    t[0] = (t[1], t[3])


def p_tipo_dado(t):
    '''
    TIPO_DADO : INTEGER_TYPE
              | REAL_TYPE
              | ARRAY LEFTBRACKET NUMERO RIGHTBRACKET OF TIPO_DADO
              | RECORD CAMPOS END
              | ID
    '''
    if len(t) == 2:
        t[0] = t[1]  # Retorna o tipo diretamente
    elif t[1] == 'array':
        t[0] = ('array', t[3], t[6])  # Representa um array com número e tipo de elementos
    elif t[1] == 'record':
        t[0] = ('record', t[2])  # Representa um tipo de registro com campos
    else:
        t[0] = t[1]  # Retorna o tipo identificado pelo ID


def p_campos(t):
    '''
    CAMPOS : ID COLON TIPO_DADO LISTA_CAMPOS
    '''
    t[0] = [(t[1], t[3])] + t[4]


def p_lista_campos(t):
    '''
    LISTA_CAMPOS : SEMICOLON CAMPOS LISTA_CAMPOS
                | empty
    '''
    if len(t) > 2:
        t[0] = t[2] + t[3]
    else:
        t[0] = []


def p_def_var(t):
    '''
    DEF_VAR : VAR VARIAVEL SEMICOLON LIST_VAR
            | empty
    '''
    if len(t) > 2:
        t[0] = ('DEF_VAR', [t[2], *t[4]])
    else:
        t[0] = None


def p_list_var(t):
    '''
    LIST_VAR : VARIAVEL SEMICOLON LIST_VAR
             | empty
    '''
    if len(t) > 2:
        t[0] = (t[1], *t[3])
    else:
        t[0] = ()


def p_variavel(t):
    '''
    VARIAVEL : LISTA_ID COLON TIPO_DADO
    '''
    if len(t) == 2:
        t[0] = ('VARIAVEL', t[1], None)
    else:
        t[0] = ('VARIAVEL', t[1], t[3])


def p_lista_id(t):
    '''
    LISTA_ID : ID COMMA LISTA_ID
             | ID
    '''
    if len(t) == 4:
        t[0] = t[1] + ', ' + t[3]
    else:
        t[0] = t[1]


def p_def_rot(t):
    '''
    DEF_ROT : NOME_ROTINA DEF_VAR BLOCO DEF_ROT
            | empty
    '''
    if len(t) == 5:
        t[0] = ('DEF_ROT', t[1], t[2], t[3], t[4])
    else:
        t[0] = () 


def p_nome_rotina(t):
    '''
    NOME_ROTINA : FUNCTION ID PARAM_ROT COLON TIPO_DADO
                | PROCEDURE ID PARAM_ROT
    '''
    if len(t) > 4:
        t[0] = ('NOME_ROTINA', t[1], t[2], t[3], t[4], t[5])
    else:
        t[0] = ('NOME_ROTINA', t[1], t[2], t[3])


def p_param_rot(t):
    '''
    PARAM_ROT : LEFTPARENTHESIS CAMPOS RIGHTPARENTHESIS
              | empty
    '''
    if len(t) > 2:
        t[0] = ('PARAM_ROT', t[1], t[2], t[3])
    else:
        t[0] = None


def p_bloco(t):
    '''
    BLOCO : BEGIN COMANDO SEMICOLON LISTA_COM END
          | COLON COMANDO
    '''
    if len(t) == 6:
        t[0] = ('BLOCO', [t[2], *t[4]])
    else:
        t[0] = ('BLOCO', t[2])


def p_lista_com(t):
    '''
    LISTA_COM : COMANDO SEMICOLON LISTA_COM
              | empty
    '''
    if len(t) > 2:
        t[0] = (t[1], *t[3])
    else:
        t[0] = ()


def p_comando(t):
    '''
    COMANDO : ID NOME ATRIB
            | WHILE EXP_LOGICA DO BLOCO
            | IF EXP_LOGICA THEN BLOCO ELSE_RULE
            | RETURN EXP_LOGICA
            | WRITE EXP_MAT
            | READ ID NOME
    '''
    t[0] = ('COMANDO', *t[1:])


def p_atrib(t):
    '''
    ATRIB : ASSIGNMENT EXP_MAT
          | empty
    '''
    if len(t) > 2:
        t[0] = ('ATRIB', t[2])
    else:
        t[0] = None


def p_else_rule(t):
    '''
    ELSE_RULE : ELSE BLOCO
              | empty
    '''
    if len(t) > 2:
        t[0] = ('ELSE_RULE', t[2])
    else:
        t[0] = None


def p_lista_param(t):
    '''
    LISTA_PARAM : PARAMETRO COMMA LISTA_PARAM
                | PARAMETRO
                | empty
    '''
    if len(t) == 4:
        t[0] = [t[1]] + t[3]
    elif len(t) == 2:
        t[0] = [t[1]]
    else:
        t[0] = []


def p_op_logico(t):
    '''
    OP_LOGICO : GREATERTHAN
              | LESSTHAN
              | COMPARE
              | NOTEQUAL
              | GREATERTHANOREQUAL
              | LESSTHANOREQUAL
    '''
    t[0] = t[1]


def p_exp_logica(t):
    '''
    EXP_LOGICA : EXP_MAT OP_LOGICO EXP_LOGICA
               | EXP_MAT
    '''
    if len(t) > 2:
        t[0] = (t[2], t[1], t[3])
    else:
        t[0] = t[1]


def p_exp_mat(t):
    '''
    EXP_MAT : PARAMETRO OP_MAT EXP_MAT
            | PARAMETRO
    '''
    if len(t) > 2:
        t[0] = (t[2], t[1], t[3])
    else:
        t[0] = t[1]


def p_op_mat(t):
    '''
    OP_MAT : PLUS
           | MINUS
           | TIMES
           | DIVIDE
           | MODULO
    '''
    t[0] = t[1]


def p_parametro(t):
    '''
    PARAMETRO : ID NOME
              | NUMERO
    '''
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[0] = (t[1], t[2])


def p_nome(t):
    '''
    NOME : DOT ID NOME
         | LEFTBRACKET PARAMETRO RIGHTBRACKET
         | LEFTPARENTHESIS LISTA_PARAM RIGHTPARENTHESIS
         | empty
    '''
    if len(t) == 2:
        t[0] = None
    elif len(t) == 4:
        t[0] = t[2]
    else:
        t[0] = (t[1], t[2], t[3], t[4])


def p_id(t):
    'ID : IDENTIFIER'
    t[0] = t[1]


def p_numero(t):
    '''NUMERO : INTEGER_NUM
              | REAL_NUM'''
    t[0] = t[1]


def p_error(t):
    parser.errok()
    if not t:
        raise ValueError()
    if t.lineno not in log_erros.keys():
        log_erros[t.lineno] = {
            "valor": f"{t.value}",
            "colunas": [t.lexpos + i for i in range(len(t.value))]
        }
    else:
        aux_column = log_erros[t.lineno]["colunas"] + [t.lexpos - 1] + [t.lexpos + i for i in range(len(str(t.value)))]
        if not lista_continua(aux_column):
            log_erros[t.lineno]["valor"] += f" {t.value}"
        log_erros[t.lineno]["colunas"] = aux_column


parser = yacc.yacc(method='LALR', start='PROGRAMA')
