import ast
import json

from semantic_aux import get_info

declared_identifiers = set()
type_ = {
    "int": int,
    "str": str,
    "list": list,
    "record": dict,
    "bool": bool,
    "real": float,
}


def check_declaration(_iter):
    """
    Checar se o identificador atribuído já foi utilizado anteriormente no mesmo escopo.
    """
    ids = set()
    for _id in _iter:
        if _id.get("local"):
            if (_id["nome"], _id["local"]) in ids:
                raise ValueError(f"Identificador '{_id['nome']}' já foi declarado.")
            else:
                ids.add((_id["nome"], _id["local"]))
        else:
            if _id["nome"] in ids:
                raise ValueError(f"Identificador '{_id['nome']}' já foi declarado.")
            else:
                ids.add(_id["nome"])

def check_type_compatibility(left_expr, right_expr, operation):
    """
    TODO - Checar se a operação matemática faz sentido
    """
    left_type = type(left_expr)
    right_type = type(right_expr)

    if left_type != right_type:
        raise ValueError(
            f"Operação '{operation}' entre tipos \
            incompatíveis: {left_type} e {right_type}."
        )


def check_assignment(variable):
    """
    TODO - Checar se a variável atribuída existe
    """
    if variable not in declared_identifiers:
        raise ValueError(
            f"Tentativa de atribuir a uma variável não \
            declarada: {variable}."
        )


def check_variable_usage(variable):
    """
    TODO - Checar se a variável declara foi utilizada
    """
    if variable not in declared_identifiers:
        raise ValueError(
            f"Tentativa de usar uma variável não \
            declarada: {variable}."
        )


def check_function_call(name, arguments):
    """
    TODO - Checar se a função chamada existe, se a quantidade de parâmetros esta corretos e se os tipos estão corretos
    """
    function_info = get_info(name, "func")

    if not function_info:
        raise ValueError(f"Chamada para função desconhecida: {name}.")

    expected_num_params = len(function_info["parametros"])
    actual_num_params = len(arguments)

    if expected_num_params != actual_num_params:
        raise ValueError(
            f"Chamada para {name} com número incorreto de parâmetros. \
            Esperado: {expected_num_params}, Obtido: {actual_num_params}."
        )

    for arg, param_type in zip(arguments, function_info["parameters"]):
        arg_type = type(arg)
        if arg_type != param_type:
            raise ValueError(
                f"Tipo de parâmetro incorreto na chamada para {name}. \
                Esperado: {param_type}, Obtido: {arg_type}."
            )


def check_logical_expression(expr):
    """
    TODO - Checar se a expressão lógica retorna um booleano corretamente.
    """
    if type(expr) is bool:
        raise ValueError("A expressão lógica deve resultar em um valor booleano.")


def check_array(name):
    """
    TODO - Checar se os valores atribuídos ao array respeitam o tipo e o tamanho
    """
    array_info = get_info(name, "array")

    if not array_info:
        raise ValueError(f"Array desconhecido: {name}.")

    for index in array_info["valores"]:
        if type_[array_info["tipo"]] is not type(index):
            raise ValueError(
                f"O índice do array deve ser do tipo {array_info['tipo']}."
            )


def check_record_field_access(name, field):
    """
    TODO - Checar se o campo que está sendo acessado existe no record
    """
    record_info = get_info(name, "record")

    if not record_info:
        raise ValueError(
            f"Tentativa de acessar campos de um registro \
            desconhecido: {name}."
        )

    if field not in record_info["fields"]:
        raise ValueError(f"Campo desconhecido '{field}' em {name}.")


def check_function_return(name, return_expr):
    """
    TODO - Checar se o retorno das funções é de mesmo tipo que o retorno salvo para a função
    """
    function_info = get_info(name, "func")

    if not function_info:
        raise ValueError(f"Tentativa de retornar de uma função desconhecida: {name}.")

    expected_return_type = function_info["return_type"]
    actual_return_type = type(return_expr)

    if expected_return_type != actual_return_type:
        raise ValueError(
            f"Tipo de retorno incorreto para a função {name}. \
        Esperado: {expected_return_type}, Obtido: {actual_return_type}."
        )


def salvar_json_const(consts: list):
    json_const = []
    for const in consts:
        if const[0] != "CONSTANTE":
            raise ValueError(f"Constante {const[1]} não declarada como Constante!")
        if const[2][0] != "CONST_VALOR":
            raise ValueError(
                f"Valor da constante {const[1]} \
                não definido como valor de constante!"
            )
        json_const.append({"nome": const[1], "valor": const[2][1]})

    with open("json_const.json", "w") as jc:
        json.dump(json_const, jc, indent=4)
        jc.close()
    return json_const


def salvar_json_tipos(tipos: list):
    json_array = []
    json_record = []

    for tipo in tipos:
        if tipo[1][0] == "array":
            json_array.append({
                "nome": tipo[0],
                "tipo": tipo[1][2],
                "tamanho": tipo[1][1],
                "valores": [],
            })
        if tipo[1][0] == "record":
            json_record.append({
                "nome": tipo[0],
                "valores": {
                    nome_campo: {"tipo": tipo_campo}
                    for nome_campo, tipo_campo in tipo[1][1]
                }
            })

    with open("json_array.json", "w") as ja:
        json.dump(json_array, ja, indent=4)
        ja.close()

    with open("json_record.json", "w") as jr:
        json.dump(json_record, jr, indent=4)
        jr.close()
    
    return json_array, json_record


def salvar_json_var(vars: list):
    """
    {
        "tipo": "record",
        "valor": "dict_1",
        "estrutura": json_record.get("dict_1").get("valores"),
        "local": "global"
    }
    """
    json_var = []

    for var in vars:
        if var[0] != "VARIAVEL":
            raise ValueError(f"Variável {var[1]} não declarada como variável!")

        tipo = var[2]
        valor = None
        estrutura = None

        json_found = {
            "array": get_info(var[2], "array"),
            "record": get_info(var[2], "record"),
            "const": get_info(var[2], "const"),
        }
        for key in json_found.keys():
            if json_found[key]:
                tipo = key
                valor = var[2]
                estrutura = json_found[key]

        if "," in var[1]:
            multi_var = var[1].split(",")
            for v in multi_var:
                json_var.append({
                    "nome": v.strip(),
                    "tipo": tipo,
                    "valor": valor,
                    "estrutura": estrutura,
                    "local": "global"
                })
        else:
            json_var.append({
                "nome": var[1].strip(),
                "tipo": tipo,
                "valor": valor,
                "estrutura": estrutura,
                "local": "global"
            })

    with open("json_var.json", "w") as jv:
        json.dump(json_var, jv, indent=4)
    return json_var


def criar_json_function(func: tuple):
    if len(func) == 0:
        return []

    return [{
        "nome": func[1][2],
        "dados": {
            "rotina": func[1][1],
            "params": {k: v for k, v in func[1][3][2]}
            if func[1][3] is not None
            else {},
            "returns": func[1][5] if len(func[1]) == 6 else None,
        },
        "comandos": criar_json_comando(separar_blocos(func))
    }] + criar_json_function(func[4])


def salvar_json_function(func: tuple):
    json_func = criar_json_function(func)
    with open("json_function.json", "w") as jf:
        json.dump(json_func, jf, indent=4)
    return json_func


def criar_json_var_function(func: tuple):
    if len(func) == 0:
        return []

    if not func[2]:
        return criar_json_var_function(func[4])

    json_var = []

    if func[2][1][0][0] != "VARIAVEL":
        raise ValueError(f"Variável {func[2][1][0][1]} não declarada como variável!")

    tipo = func[2][1][0][2]
    valor = None
    estrutura = None

    json_found = {
        "array": get_info(func[2][1][0][2], "array"),
        "record": get_info(func[2][1][0][2], "record"),
        "const": get_info(func[2][1][0][2], "const"),
    }
    for key in json_found.keys():
        tipo = key
        valor = func[2][1][0][2]
        estrutura = json_found[key]

    if "," in func[2][1][0][1]:
        multi_var = func[2][1][0][1].split(",")
        for v in multi_var:
            json_var.append({
                "nome": v.strip(),
                "tipo": tipo,
                "valor": valor,
                "estrutura": estrutura,
                "local": func[1][2]
            })
    else:
        json_var.append({
            "nome": func[2][1][0][1].strip(),
            "tipo": tipo,
            "valor": valor,
            "estrutura": estrutura,
            "local": func[1][2]
        })

    return json_var + criar_json_var_function(func[4])


def salvar_json_var_function(func: tuple):
    with open("json_var.json", "r") as jf:
        json_var = json.load(jf)
        jf.close()
    json_var += criar_json_var_function(func)
    with open("json_var.json", "w") as jf:
        json.dump(json_var, jf, indent=4)
    return json_var


def criar_json_comando(comandos: list):
    json_comandos = []

    for comando in comandos:
        json_comandos.append({
            'nome_comando': comando.get("nome_comando"),
            'exp': tratar_exp(comando.get('exp')) if comando.get('exp') else None,
            'variavel': comando.get('variavel'),
            'nome': comando.get('nome'),
            'sub_comandos': comando.get('subcomandos'),
            'sub_blocos': comando.get('sub_blocos'),
        })
    
    return json_comandos


def tratar_exp(exp: tuple):
    print(f"Ele entrou assim: {exp}")
    if not isinstance(exp, int) and exp[0] == "ATRIB":
        exp = exp[1]
    if isinstance(exp, int):
        print(f"E saiu assim 1: {exp}")
        return exp
    elif len(exp) == 2:
        if not exp[1]:
            print(f"E saiu assim 2: {exp[0]}")
            return exp[0]
        elif isinstance(exp[1], list):
            for count, xp in enumerate(exp[1]):
                exp[1][count] = xp[0] if not xp[1] else xp
            return exp[0], exp[1]
        return exp
    elif isinstance(exp, tuple):
        exp = [exp[1], exp[0], exp[2]]
        if isinstance(exp[0], tuple):
            if exp[0][1] is None:
                exp[0] = exp[0][0]
            elif isinstance(exp[0][1], list):
                for count, xp in enumerate(exp[0][1]):
                    exp[0][1][count] = xp[0] if not xp[1] else xp
        if isinstance(exp[2], tuple):
            if exp[2][1] is None:
                exp[2] = exp[2][0]
            elif isinstance(exp[2][1], list):
                for count, xp in enumerate(exp[2][1]):
                    exp[2][1][count] = xp[0] if not xp[1] else xp
        print(f"E saiu assim 3: {exp}")
        return exp


def salvar_json_comandos(comandos: list):
    json_comandos = criar_json_comando(comandos)
    with open("json_comando.json", "w") as jc:
        json.dump(json_comandos, jc, indent=4)
    return json_comandos


def separar_defs(arvore):
    defs = {}
    def_names = {
        "DEF_CONST": "json_const",
        "DEF_TIPOS": "json_tipos",
        "DEF_VAR": "json_var",
        "DEF_ROT": "json_func",
    }

    for item in arvore[0]:
        if (
            isinstance(item, tuple)
            and len(item) > 0
            and isinstance(item[0], str)
            and item[0].startswith("DEF")
        ):
            defs[def_names[item[0]]] = item[1:][0] if item[0] != "DEF_ROT" else item

    return defs


def separar_blocos(arvore):
    blocos = []

    for item in arvore:
        if isinstance(item, tuple) and len(item) > 0 and isinstance(item[0], str) and item[0] == 'BLOCO':
            comandos = item[1]
            blocos += separar_comandos(comandos)

    return blocos


def separar_comandos(comandos):
    resultado = []

    for comando in comandos:
        if comando[1] == "while":
            _, nome_comando, exp, sub_comandos, sub_bloco = comando
            resultado.append({
                'nome_comando': nome_comando,
                'exp': exp,
                'sub_comandos': sub_comandos,
                'sub_blocos': separar_blocos(sub_bloco)
            })
        elif comando[1] == "if":
            if len(comando) == 6:
                _, nome_comando, exp, sub_comandos, sub_bloco, _else = comando
                resultado.append({
                    'nome_comando': nome_comando,
                    'exp': exp,
                    'sub_comandos': sub_comandos,
                    'sub_blocos': separar_blocos(sub_bloco),
                    'else': separar_blocos(_else[1])
                })
            else:
                _, nome_comando, exp, sub_comandos, sub_bloco = comando
                resultado.append({
                    'nome_comando': nome_comando,
                    'exp': exp,
                    'sub_comandos': sub_comandos,
                    'sub_blocos': separar_blocos(sub_bloco)
                })
        elif comando[1] == "return" or comando[1] == "write":
            _, nome_comando, exp = comando
            resultado.append({
                'nome_comando': nome_comando,
                'exp': exp
            })

        elif comando[1] == "read":
            _, nome_comando, variavel, nome = comando
            resultado.append({
                'nome_comando': nome_comando,
                'variavel': variavel,
                'nome': nome
            })
        
        else:
            _, variavel, nome, exp = comando
            resultado.append({
                'nome_comando': "ATRIB",
                'variavel': variavel,
                'nome': nome,
                'exp': exp[1] if exp else None
            })


    return resultado


def read_tree(name: str):
    with open(name, "r") as f:
        tree = f.read()

    arvore = ast.literal_eval(tree)
    defs_separadas = separar_defs(arvore)
    json_const = salvar_json_const(defs_separadas["json_const"])
    json_array, json_record = salvar_json_tipos(defs_separadas["json_tipos"])
    json_var = salvar_json_var(defs_separadas["json_var"])
    json_func = salvar_json_function(defs_separadas["json_func"])
    json_var = salvar_json_var_function(defs_separadas["json_func"])

    # check_declaration #
    for json_data in [json_const, json_array, json_record, json_var, json_func]:
        check_declaration(json_data)

    comandos = separar_blocos(arvore)
    json_comandos = salvar_json_comandos(comandos)

    # check_type_compatibility #


    # check_assignment #


    # check_variable_usage #


    # check_function_call #


    # check_logical_expression #


    # check_array #


    # check_record_field_access #


    # check_function_return #


read_tree("transcricao.txt")
