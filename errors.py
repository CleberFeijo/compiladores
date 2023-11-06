# #!/usr/bin/python
#
# def unknownSignal(t):
#     print("Unknown Signal at '%s', in Line %d , Column %d!" % (t.value, t.lineno, t.lexpos))
#
#
# def unknownError(t):
#     if t:
#         print("Syntax error at '%s', in Line %d , Column %d" % (t.value, t.lineno, t.lexpos))
#     else:
#         print("Syntax error at EOF")
#         raise SystemExit
#
#
# def VarDecError(t):
#     print("Declaration Variavel Error at '%s', in Line %d , Column %d" % (t.value, t.lineno, t.lexpos))
#
#
# def NoSemicolonError(t):
#     print("No Semicolon Error , in Line %d , Column %d" % (t.lineno(0), t.lexpos(0)))
#
#
# def NoTypeError(t):
#     print("No type defined Error , in Line %d , Column %d" % (t.lineno(0), t.lexpos(0)))
#
#
# def SameNameError(t):
#     print("Same Name Variavel Error at '%s', in Line %d , Column %d" % (t.value, t.lineno, t.lexpos))
