#
#
# class Escopo(object):
#     """docstring for Escopo."""
#     names = {}
#
#     def __init__(self, name):
#         super(Escopo, self).__init__()
#         self.name = name
#
#     def add(self, value):
#         for element in value:
#             if self.names.get(element):  # has a declaration with this name
#                 print("Same Name Variavel Error " + str(element))
#             else:
#                 self.names[element] = value[element]
#             return
#
#     def show(self, d):
#         try:
#             return self.names[d].value
#         except:
#             for element in self.names:
#                 try:
#                     return self.names[element].escopo.show(d)
#                 except:
#                     continue
#         return None
#
#     def change(self, v, value):
#         self.names[v].value = value
#
#     def all(self):
#         return self.names
#
#     def __str__(self):
#         tmp = self.name+"\n"
#         tmp += "____________________________________________________________\n"
#         for element in self.names:
#             tmp += str(self.names[element])+"\n"
#
#         return tmp
#
#     def name(self):
#         return str(self.names)
#
#
# class Declaration(object):
#     """docstring for Declaration."""
#     name = ''
#
#     def __init__(self):
#         super(Declaration, self).__init__()
#
#     def __str__(self):
#         return self.name
#
#
# class Variable(Declaration):
#     """Exclusive class for control variables"""
#     name = ''
#     type = ''
#     value = None
#
#     def __init__(self, name, type_, value):
#         super(Variable, self).__init__()
#         self.name = name
#         self.type = type_
#         self.value = value
#         self.def_type(type)
#
#     def def_type(self, type_):
#         self.type = type_
#         if not self.value:
#             if type_ == "int":
#                 self.value = 0
#             elif type_ == "bool":
#                 self.value = False
#             elif type_ == "string":
#                 self.value = ''
#
#     def __str__(self):
#         return "Variable: " + self.name + "\n\tType: " + str(self.type) + \
#                "\n\tValue: " + str(self.value)
#
#     def __repr__(self):
#         return "|"+self.name + "," + str(self.type) + "," + str(self.value)+"|"
#
#
# class Function(Declaration):
#     """docstring for Function."""
#     def __init__(self, name, type_, parametros, block):
#         super(Function, self).__init__()
#         self.name = name
#         self.type = type_
#         self.parametros = parametros
#         self.block = block
#
#     def __str__(self):
#         tmp = "Function: " + self.name + " \n\tType:" + self.type + \
#               "\n\tparametros:"
#         tmp += str(self.parametros) + " \n\t" + str(self.block)
#         return tmp
#
#     def __repr__(self):
#         return "|" + self.name + "," + self.type + "," + \
#                str(self.parametros) + "|"
#
#
# class Procedure(object):
#     """docstring for Procedure."""
#     def __init__(self, name, parametros, block):
#         super(Procedure, self).__init__()
#         self.name = name
#         self.parametros = parametros
#         self.block = block
#
#     def __str__(self):
#         return self.name + " " + str(self.parametros)
#
#     def __repr__(self):
#         return "|" + self.name + "," + str(self.parametros) + "|"
#
#
# class Block(object):
#     """docstring for Block."""
#     def __init__(self, pai, variaveis, statements):
#         super(Block, self).__init__()
#         self.pai = pai
#         tmp = None
#         self.escopo = tmp
#         self.statements = statements
#
#     def __str__(self):
#         return "Block " + self.pai + ": " + str(self.escopo) + \
#                " \n\tStatements:" + str(self.statements)
#
#     def __repr__(self):
#         return "|" + self.escopo + " \n\tStatements:\n" + \
#                str(self.statements) + "|"
