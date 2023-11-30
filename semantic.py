import ast
import json

from semantic_aux import get_info

declared_identifiers = set()
type_ = {
    "integer": int,
    "string": str,
    "array": "array",
    "record": "record",
    "bool": bool,
    "real": float,
    int: int,
    str: str,
    list: "array",
    bool: bool,
    float: float
}
ids = set()


def check_declaration(_iter):
    """
    Checar se o identificador atribuído já foi utilizado anteriormente no mesmo escopo.
    """
    for _id in _iter:
        if _id.get("local"):
            if (_id["nome"], _id["local"]) in ids:
                raise ValueError(f"Identificador '{_id['nome']}' já foi declarado.")
            else:
                ids.add((_id["nome"], _id["local"]))
        else:
            if (_id["nome"], "global") in ids:
                raise ValueError(f"Identificador '{_id['nome']}' já foi declarado.")
            else:
                ids.add((_id["nome"], "global"))



def create_atribs(
    json_functions: list,
    json_variaveis: list,
    json_consts: list
):
    global atribuiveis
    atribuiveis = {}
    for var in json_variaveis:
        nome = var["nome"]
        if var["local"] != "global":
            nome = var["nome"] + "." + var["local"]
        atribuiveis[nome] = {
            "tipo": var["tipo"],
            "local": var["local"],
            "estrutura": var["estrutura"],
            "from": "var"
        }
    for func in json_functions:
        atribuiveis[func["nome"]] = {
            "tipo": func["dados"]["returns"],
            "params": func["dados"]["params"],
            "local": "global",
            "from": "func"
        }
    for const in json_consts:
        atribuiveis[const["nome"]] = {
            "tipo": type(const["valor"]),
            "local": "global",
            "from": "const"
        }
    for func in json_functions:
        for param in func["dados"]["params"].keys():
            name = param + "." + func["nome"]
            atribuiveis[name] = {
                "tipo": func["dados"]["params"][param],
                "local": func["nome"],
                "from": "var"
            }


def check_comands(
    json_comandos: list,
    json_functions: list
):
    """
    Checar se a variável atribuída existe e se o tipo é igual
    """
    for comando in json_comandos:
        if comando["nome_comando"] != "ATRIB":
            if (comando["variavel"], "global") not in ids:
                raise ValueError(
                    f"Tentativa de atribuir a uma variável não \
                    declarada: {comando['variavel']}, local: global."
                )
            exp_type = check_exp(comando["exp"], "global")
            if type_[atribuiveis[comando["variavel"]]["tipo"]] != type_[exp_type]:
                raise ValueError(
                    f"Tentativa de atribuir a uma variável um valor \
                    não condizente: Exp: {comando} \
                    Tipo_var: {type_[atribuiveis[comando['variavel']]['tipo']]}.\
                    Tipo_atrib: {type_[exp_type]}"
                )
        else:
            check_exp(comando["exp"], "global")
            if comando["nome"]:
                check_record_field_access(comando["variavel"], comando['nome'])

    for func in json_functions:
        for comando in func["comandos"]:
            if comando["nome_comando"] == "ATRIB":
                if (comando["variavel"], func["nome"]) not in ids:
                    raise ValueError(
                        f"Tentativa de atribuir a uma variável não \
                        declarada: {comando['variavel']}, local: {func['nome']}."
                    )
                exp_type = check_exp(comando["exp"], func["nome"])
                if not atribuiveis.get(comando["variavel"]):
                    comando["variavel"] += "."+func["nome"]
                try:
                    if type_[atribuiveis[comando["variavel"]]["tipo"]] != type_[exp_type]:
                        raise ValueError(
                            f"Tentativa de atribuir a uma variável um valor \
                            não condizente: Exp: {comando} \
                            Tipo_var: {type_[atribuiveis[comando['variavel']]['tipo']]}.\
                            Tipo_atrib: {type_[exp_type]}"
                        )
                except KeyError:
                    is_array = get_info(atribuiveis[comando["variavel"]]["tipo"], "array")
                    is_record = get_info(atribuiveis[comando["variavel"]]["tipo"], "record")
                    if is_array:
                        atribuiveis[comando["variavel"]]["tipo"] = "array"
                    elif is_record:
                        atribuiveis[comando["variavel"]]["tipo"] = "record"
                    if type_[atribuiveis[comando["variavel"]]["tipo"]] != type_[exp_type]:
                        raise ValueError(
                            f"Tentativa de atribuir a uma variável um valor \
                            não condizente: Exp: {comando} \
                            Tipo_var: {type_[atribuiveis[comando['variavel']]['tipo']]}.\
                            Tipo_atrib: {type_[exp_type]}"
                        )
            else:
                check_exp(comando["exp"], func["nome"])
                if comando["nome"]:
                    check_record_field_access(comando["variavel"], comando['nome'])


def check_exp(exp: list | int | str | bool, local: str) -> str:
    if not isinstance(exp, list) and not isinstance(exp, tuple):
        if isinstance(exp, str):
            var = exp
            is_list = False
            index = None
            if "[" in exp:
                var = exp.split('[')[0]
                index = int(exp.split('[')[1].replace(']', ''))
                if index < 1:
                    raise ValueError(
                        f"Indice fora de alcance na exp {exp}."
                    )
                is_list = True
            if atribuiveis.get(var):
                if is_list and atribuiveis[var]['tipo'] != "array":
                    if not get_info(atribuiveis[var]['tipo'], "array"):
                        raise ValueError(
                            f"Utilização errada do indice ([])  na exp {exp}. tipo {atribuiveis[var]['tipo']}"
                        )
                    atribuiveis[var]['estrutura'] = get_info(atribuiveis[var]['tipo'], "array")
                    atribuiveis[var]["tipo"] = atribuiveis[var]['estrutura']["tipo"]
                if is_list and atribuiveis[var]['estrutura']['tamanho'] < index:
                    raise ValueError(
                        f"Indice fora de alcance."
                    )
                return atribuiveis[var]["tipo"]
            elif atribuiveis.get(var+"."+local):
                var += "." + local
                if is_list and atribuiveis[var]['tipo'] != "array":
                    if not get_info(atribuiveis[var]['tipo'], "array"):
                        raise ValueError(
                            f"Utilização errada do indice ([])  na exp {exp}. tipo {atribuiveis[var]['tipo']}"
                        )
                    atribuiveis[var]['estrutura'] = get_info(atribuiveis[var]['tipo'], "array")
                    atribuiveis[var]["tipo"] = atribuiveis[var]['estrutura']["tipo"]
                if is_list and atribuiveis[var]['estrutura']['tamanho'] < index:
                    raise ValueError(
                        f"Indice fora de alcance  na exp {exp}."
                    )
                return atribuiveis[var]["tipo"]
        return type(exp)

    if isinstance(exp[0], str) and isinstance(exp[1], list):
        if atribuiveis.get(exp[0]):
            if atribuiveis[exp[0]]['from'] == "func":
                if len(exp[1]) != len(atribuiveis[exp[0]]['params']):
                    raise ValueError(
                        f"Quantidade errada de parâmetros sendo passados para função {exp[0]}. \
                        QTD_Aceita: {len(atribuiveis[exp[0]]['params'])}, \
                        QTD_Enviada: {len(exp[1])}."
                    )
                for count, xp in enumerate(exp[1]):
                    if check_exp(xp, local) != list(atribuiveis[exp[0]]['params'].values())[count]:
                        if check_exp(xp, local) not in ["array", "record"]:
                            raise ValueError(
                                f"Tipo errado de parâmetros sendo passados para função {exp[0]}. \
                                Param_Aceito: {list(atribuiveis[exp[0]]['params'].values())[count]}, \
                                Param_Enviado: {xp}, tipo: {check_exp(xp, local)}. Local: {local}"
                            )
                        elif not get_info(list(atribuiveis[exp[0]]['params'].values())[count], check_exp(xp, local)):
                            raise ValueError(
                                f"Tipo errado de parâmetros sendo passados para função {exp[0]}. \
                                Param_Aceito: {list(atribuiveis[exp[0]]['params'].values())[count]}, \
                                Param_Enviado: {xp}, tipo: {check_exp(xp, local)}. Local: {local}"
                            )
                return atribuiveis[exp[0]]['tipo']
            raise ValueError(
                f"Tentativa de passar parâmetros para uma não função."
            )
        raise ValueError(
            f"Tentativa de atribuir uma função não \
            declarada: {exp[0]}."
        )
    if len(exp) > 2:
        types = []
        for i in range(0, len(exp), 2):
            if isinstance(exp[i], list) or isinstance(exp[i], tuple):
                types.append(check_exp(exp[i], local))
            elif atribuiveis.get(exp[i]):
                types.append(type_[atribuiveis[exp[i]]['tipo']])
            elif atribuiveis.get(str(exp[i]) + "." + local):
                types.append(type_[atribuiveis[str(exp[i]) + "." + local]['tipo']])
            else:
                types.append(type(exp[i]))
        for elem in types:
            if not type_[elem] == type_[types[0]]:
                raise ValueError(
                    f"Expressão com variáveis/funções não compatíveis. \
                    Expressão: {exp}"
                )

        return types[0]


def check_record_field_access(var, nome):
    """
    Checar se o campo que está sendo acessado existe no record
    """
    record_info = atribuiveis.get(var)

    if not record_info or record_info["tipo"] != "record":
        raise ValueError(
            f"Foi utilizado (.) em uma variável que não é record: {var}."
        )

    if nome not in record_info["estrutura"]["valores"].keys():
        raise ValueError(f"Campo desconhecido '{nome}' em {var}.")


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
                "valores": []
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
                    "tipo": tipo if tipo != "const" else valor,
                    "valor": valor if tipo != "const" else tipo,
                    "estrutura": estrutura,
                    "local": "global"
                })
        else:
            json_var.append({
                "nome": var[1].strip(),
                "tipo": tipo if tipo != "const" else valor,
                "valor": valor if tipo != "const" else tipo,
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
                "tipo": tipo if tipo != "const" else valor,
                "valor": valor if tipo != "const" else tipo,
                "estrutura": estrutura,
                "local": func[1][2]
            })
    else:
        json_var.append({
            "nome": func[2][1][0][1].strip(),
            "tipo": tipo if tipo != "const" else valor,
            "valor": valor if tipo != "const" else tipo,
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
            'exp': tratar_exp(comando.get('exp')) if comando.get('exp') is not None else None,
            'variavel': comando.get('variavel'),
            'nome': comando.get('nome'),
            'sub_comandos': comando.get('subcomandos'),
            'sub_blocos': comando.get('sub_blocos'),
        })
    
    return json_comandos


def tratar_exp(exp: tuple):
    if not isinstance(exp, int) and exp[0] == "ATRIB":
        exp = exp[1]
    if isinstance(exp, int):
        return exp
    if isinstance(exp, bool):
        return exp
    elif len(exp) == 2:
        if exp[1] is None:
            return exp[0]
        elif isinstance(exp[1], list):
            for count, xp in enumerate(exp[1]):
                exp[1][count] = xp[0] if not xp[1] else xp
            return exp[0], exp[1]
        elif isinstance(exp[1], int):
            return f"{exp[0]}[{exp[1]}]"
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
                'nome': nome if isinstance(nome, str) else None,
                'exp': exp[1] if exp else None
            })

    return resultado


def read_tree(name: str):
    with open(name, "r") as f:
        tree = f.read()

    arvore = ast.literal_eval(tree)
    defs_separadas = separar_defs(arvore)
    count = 0
    json_const = salvar_json_const(defs_separadas["json_const"])
    json_array, json_record = salvar_json_tipos(defs_separadas["json_tipos"])
    json_var = salvar_json_var(defs_separadas["json_var"])
    json_func = salvar_json_function(defs_separadas["json_func"])
    json_var = salvar_json_var_function(defs_separadas["json_func"])

    for json_data in [json_const, json_array, json_record, json_var, json_func]:
        check_declaration(json_data)

    comandos = separar_blocos(arvore)
    json_comandos = salvar_json_comandos(comandos)

    create_atribs(json_func, json_var, json_const)
    check_comands(json_comandos, json_func)
