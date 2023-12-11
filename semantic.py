import ast

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


def check_exp(exp: list | int | str | bool, local: str, atribuiveis: dict) -> tuple:
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
            if atribuiveis.get(local).get(var):
                if is_list and atribuiveis[local][var]['tipo'] != "array":
                    if type_[atribuiveis["global"][atribuiveis[local][var]['tipo']]['tipo']] != "array":
                        raise ValueError(
                            f"Utilização errada do indice ([])  na exp {exp}. tipo {atribuiveis[local][var]['tipo']}"
                        )
                if is_list and atribuiveis["global"][atribuiveis[local][var]['tipo']]["valor"] < index:
                    raise ValueError(
                        f"Indice fora de alcance."
                    )
                return atribuiveis[local][var]['tipo'], exp
        return type(exp), exp

    elif isinstance(exp[0], str) and isinstance(exp[1], list):
        if not atribuiveis.get(exp[0]):
            raise ValueError(
                f"Tentativa de atribuir uma função não \
                declarada: {exp[0]}."
            )
        params = [param["tipo"] for param in atribuiveis.get(exp[0]).values() if param.get("from") == "func"]
        if len(exp[1]) != len(params):
            raise ValueError(
                f"Quantidade errada de parâmetros sendo passados para função {exp[0]}. \
                QTD_Aceita: {len(params)}, \
                QTD_Enviada: {len(exp[1])}."
            )
        for count, xp in enumerate(exp[1]):
            if check_exp(xp, local, atribuiveis)[0] != params[count]:
                if type_[check_exp(xp, local, atribuiveis)[0]] not in ["array", "record"]:
                    raise ValueError(
                        f"Tipo errado de parâmetros sendo passados para função {exp[0]}. \
                        Param_Aceito: {params[count]}, \
                        Param_Enviado: {xp}, tipo: {check_exp(xp, local, atribuiveis)[0]}. Local: {local}"
                    )
                elif type_[atribuiveis["global"][params[count]]["tipo"]] != type_[check_exp(xp, local, atribuiveis)[0]]:
                    raise ValueError(
                        f"Tipo errado de parâmetros sendo passados para função {exp[0]}. \
                        Param_Aceito: {params[count]}, \
                        Param_Enviado: {xp}, tipo: {check_exp(xp, local, atribuiveis)}. Local: {local}"
                    )
        return atribuiveis[exp[0]]['returns']["tipo"], exp
    elif len(exp) > 2:
        types = []
        for i in range(0, len(exp), 2):
            if isinstance(exp[i], list) or isinstance(exp[i], tuple):
                if not check_exp(exp[i], local, atribuiveis):
                    continue
                types.append(check_exp(exp[i], local, atribuiveis)[0])
            elif atribuiveis[local].get(exp[i]):
                types.append(type_[atribuiveis[local][exp[i]]['tipo']])
            elif isinstance(exp[i], str):
                var = exp[i]
                is_list = False
                index = None
                if "[" in exp[i]:
                    var = exp[i].split('[')[0]
                    index = exp[i].split('[')[1].replace(']', '')
                    try:
                        index = int(index)
                    except ValueError as e:
                        index = 1 if isinstance(index, str) else ""
                    if index < 1:
                        raise ValueError(
                            f"Indice fora de alcance na exp {exp[i]}."
                        )
                    is_list = True
                if atribuiveis.get(local).get(var):
                    if is_list and atribuiveis[local][var]['tipo'] != "array":
                        if type_[atribuiveis["global"][atribuiveis[local][var]['tipo']]['tipo']] != "array":
                            raise ValueError(
                                f"Utilização errada do indice ([])  na exp {exp[i]}. tipo {atribuiveis[local][var]['tipo']}"
                            )
                    if is_list and atribuiveis["global"][atribuiveis[local][var]['tipo']]["valor"] < index:
                        raise ValueError(
                            f"Indice fora de alcance."
                        )
                    types.append(atribuiveis["global"][atribuiveis[local][var]['tipo']]['tipo2'])
            else:
                types.append(type(exp[i]))
        for elem in types:
            if not type_[elem] == type_[types[0]]:
                raise ValueError(
                    f"Expressão com variáveis/funções não compatíveis. \
                    Expressão: {exp}"
                )

        return types[0], exp


def extract_function(ids: dict, transcript: str, func: tuple):
    if len(func) == 0:
        return transcript, ids

    transcript = extract_comando(separar_blocos(func), transcript, func[1][2], ids)

    return transcript, ids


def transcript_exp(exp, ids: dict, escopo: str, indent: int = 0, register: int = 6):
    if exp is None:
        return ""
    t = "\t"
    for i in range(indent):
        t += "\t"
    if not isinstance(exp, list) and not isinstance(exp, tuple):
        if isinstance(exp, str):
            if "[" in exp:
                exp_ = exp.split("[")
                index = exp_[1].replace("]", "")
                try:
                    index = 4*int(index)
                except ValueError as e:
                    index = f"4*{index}"
                exp_ = exp_[0]
                return f"pop R2, {exp_}\n{t}lod R{register}, {index}($R2)\n{t}"
            return f"pop R{register}, {exp}\n{t}" if ids.get(escopo).get(exp) and ids.get(escopo).get(exp).get("from") == "func" else f"lod R{register}, {exp}\n{t}"
        return f"lod R{register}, {exp}\n{t}"
    elif len(exp) > 2:
        trans = ""
        for i in range(0, len(exp), 2):
            if not isinstance(exp[i], list) and not isinstance(exp[i], tuple):
                trans += f"lod R{i+6}, {exp[i]}\n{t}"
            elif isinstance(exp[i][0], str) and isinstance(exp[i][1], list):
                trans += transcript_exp(exp[i], ids, escopo)
                trans += f"lod R{i + 6}, R{i + 6}\n{t}"
        for i in range(1, len(exp), 2):
            if exp[i] == "+":
                trans += f"add R{i+5}, R{i+7}\n{t}"
            if exp[i] == "-":
                trans += f"inv R{1+7}\n{t}add R{i+5}, R{i+7}\n{t}"
            if exp[i] == "/":
                trans += f"div R{i+5}, R{i+7}\n{t}"
            if exp[i] == "*":
                trans += f"lod R{len(exp)+7}, 1\n{t}inv R{len(exp)+7}\n{t}jnz pre_loop_mult, R{i+7}\n{t}lod R{i+5}, $0\n{t}pre_loop_mult:\n{t}\tadd R{i+7}, R{len(exp)+7}\n{t}\tjnz loop_mult, R{i+7}\n{t}loop_mult:\n{t}\tadd R{i+5}, R{i+5}\n{t}\tadd R{i+7}, R{len(exp)+7}\n{t}\tjnz loop_mult, R{i+7}\n{t}"
        return trans
    elif isinstance(exp[0], str) and isinstance(exp[1], list):
        trans = ""
        for i in range(len(exp[1])):
            if ids.get(exp[0]):
                params = [param for param in ids.get(exp[0]).keys() if ids.get(exp[0])[param].get("from") == "func"]
                trans += f"psh R{params[i]}, {exp[1][i]}\n{t}"
        return trans + f"jmp {exp[0]}\n{t}"


def extract_comando(comandos: list, transcript: str, escopo: str, ids: dict, indent: int = 0):
    must_psh = False
    for comando in comandos:
        t = "\t"
        for i in range(indent):
            t += "\t"
        treated_exp = check_exp(tratar_exp(comando.get('exp')), escopo, ids) if comando.get('exp') is not None else None
        if comando.get("nome_comando") == "write":
            transcript += f"{t}lod R1, {treated_exp[1]}\n{t}write R1\n"
        elif comando.get("nome_comando") == "read":
            transcript += f"{t}read {comando.get('variavel')}.{comando.get('nome')}\n{t}lod R{comando.get('variavel')}, {comando.get('variavel')}.{comando.get('nome')}\n"
        elif comando.get("nome_comando") == "ATRIB":
            must_psh = True
            if not treated_exp:
                transcript += f"{t}str R8 {comando.get('variavel')}\n"
            else:
                transcript += f"{t}{transcript_exp(treated_exp[1], ids, escopo, indent)}str R6 {comando.get('variavel')}\n"
        elif comando.get("nome_comando") == "while":
            transcript += f"{t}jmp loop\n{t}loop:\n\t"
            treated_exp = treated_exp[1]
            if treated_exp[1] == ">":
                transcript += f"{t}lod R{treated_exp[2]}, {treated_exp[0]}\n{t}\tlod R{treated_exp[0]}, {treated_exp[2]}\n{t}\tles R{treated_exp[2]}, R{treated_exp[0]}\n{t}\tjnz end_loop R{treated_exp[2]}\n"
            elif treated_exp[1] == "<":
                transcript += f"{t}lod R{treated_exp[0]}, {treated_exp[0]}\n{t}\tlod R{treated_exp[2]}, {treated_exp[2]}\n{t}\tles R{treated_exp[2]}, R{treated_exp[0]}\n{t}\tjnz end_loop R{treated_exp[2]}\n"
            elif treated_exp[1] == "=":
                transcript += f"{t}lod R{treated_exp[0]}, {treated_exp[0]}\n{t}\tlod R{treated_exp[2]}, {treated_exp[2]}\n{t}\teql R{treated_exp[2]}, R{treated_exp[0]}\n{t}\tjnz end_loop R{treated_exp[2]}\n"
            if comando.get('sub_blocos'):
                transcript = extract_comando(comando.get('sub_blocos'), transcript, escopo, ids, indent=indent+1)
            transcript += f"{t}\tjmp loop\n{t}end_loop:\n{t}"
        elif comando.get("nome_comando") == "if":
            treated_exp = treated_exp[1]
            if treated_exp[1] == ">":
                transcript += f"{t}{transcript_exp(treated_exp[2], ids, escopo, indent, register=6)}{transcript_exp(treated_exp[0], ids, escopo, indent, register=8)}les R6, R8\n"
            elif treated_exp[1] == "<":
                transcript += f"{t}{transcript_exp(treated_exp[0], ids, escopo, indent, register=6)}{transcript_exp(treated_exp[2], ids, escopo, indent, register=8)}les R6, R8\n"
            elif treated_exp[1] == "=":
                transcript += f"{t}{transcript_exp(treated_exp[0], ids, escopo, indent, register=6)}{transcript_exp(treated_exp[2], ids, escopo, indent, register=8)}eql R6, R8\n"
            transcript += f"{t}jnz then R6\n"
            transcript += f"{t}jmp else\n" if comando.get("else") else ""
            transcript += f"{t}then:\n"
            if comando.get('sub_blocos'):
                transcript = extract_comando(comando.get('sub_blocos'), transcript, escopo, ids, indent=indent+1)
            if comando.get('else'):
                transcript += f"{t}else:\n"
                transcript = extract_comando(comando.get('else'), transcript, escopo, ids, indent=indent+1)
    transcript += f"\tpsh R6\n" if must_psh and not indent else ""
    return transcript


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
            elif isinstance(exp[0][1], tuple):
                exp[0] = f"{exp[0][0]}[{exp[0][1][0]}]"
        if isinstance(exp[2], tuple):
            if exp[2][1] is None:
                exp[2] = exp[2][0]
            elif isinstance(exp[2][1], list):
                for count, xp in enumerate(exp[2][1]):
                    exp[2][1][count] = xp[0] if not xp[1] else xp
        return exp


def separar_defs(arvore, transcript: str, escopo="global", ids_: dict = None):

    ids = {escopo: {}} if not ids_ else ids_

    for item in arvore[0]:
        if (
            isinstance(item, tuple)
            and len(item) > 0
            and isinstance(item[0], str)
            and item[0].startswith("DEF")
        ):
            itens = item[1:][0] if item[0] != "DEF_ROT" else item
            if item[0] == "DEF_CONST":
                for const in itens:
                    if const[0] != "CONSTANTE":
                        raise ValueError(f"Constante {const[1]} não declarada como Constante!")
                    if const[2][0] != "CONST_VALOR":
                        raise ValueError(
                            f"Valor da constante {const[1]} \
                            não definido como valor de constante!"
                        )
                    if const[1] in ids[escopo].keys():
                        raise ValueError(f"Identificador '{const[1]}' já foi declarado.")
                    ids[escopo] |= {const[1]: {
                            "tipo": type(const[2][1]),
                            "valor": const[2][1],
                            "from": "const"
                        }
                    }
                    transcript += f"\tCONST {const[1]}: {const[2][1]}\n"
            elif item[0] == "DEF_TIPOS":
                for tipo in itens:
                    if tipo[0] in ids[escopo].keys():
                        raise ValueError(f"Identificador '{tipo[0]}' já foi declarado.")
                    if tipo[1][0] == "array":
                        transcript += f"\tARRAY {tipo[0]} {tipo[1][2]} {tipo[1][1]}\n"
                        ids[escopo] |= {tipo[0]: {
                                "tipo": list,
                                "tipo2": tipo[1][2],
                                "valor": tipo[1][1],
                                "from": "tipos"
                            }
                        }
                    elif tipo[1][0] == "record":
                        ids[escopo] |= {tipo[0]: {
                                "tipo": dict,
                                "valor": tipo[1][1],
                                "from": "tipos"
                            }
                        }
                        transcript += f"\tRECORD {tipo[0]}\n"
                        for nome_campo, tipo_campo in tipo[1][1]:
                            transcript += f"\t\t{nome_campo} {tipo_campo}\n"
            elif item[0] == "DEF_VAR":
                for var in itens:
                    if var[0] != "VARIAVEL":
                        raise ValueError(f"Variável {var[1]} não declarada como variável!")

                    tipo = var[2]
                    valor = None
                    
                    if ids[escopo].get(var[2]):
                        tipo = ids[escopo][var[2]]["tipo"] if ids[escopo][var[2]]["tipo"] not in [list, dict] else var[2]
                        valor = ids[escopo][var[2]]["valor"]
                    elif var[2] not in type_.keys():
                        raise ValueError("Tentativa de atribuir tipo não existente.")

                    if "," in var[1]:
                        multi_var = var[1].split(",")
                        for v in multi_var:
                            if v.strip() in ids[escopo].keys():
                                raise ValueError(f"Identificador '{tipo[0]}' já foi declarado.")
                            ids[escopo] |= {v.strip(): {
                                    "tipo": tipo if tipo != "const" else valor,
                                    "valor": valor if tipo != "const" else tipo,
                                    "from": "var"
                                }
                            }
                            transcript += f"\tVAR {v.strip()} {tipo if tipo != 'const' else valor}\n"
                    else:
                        if var[1].strip() in ids[escopo].keys():
                            raise ValueError(f"Identificador '{tipo[0]}' já foi declarado.")
                        ids[escopo] |= {var[1].strip(): {
                                "tipo": tipo if tipo != "const" else valor,
                                "valor": valor if tipo != "const" else tipo,
                                "from": "var"
                            }
                        }
                        transcript += f"\tVAR {var[1].strip()} {tipo}\n"
            elif item[0] == "DEF_ROT":
                if item[1][3] is not None:
                    for k, v in item[1][3][2]:
                        if ids.get(item[1][2]):
                            ids[item[1][2]] |= {
                                k: {
                                    "tipo": v,
                                    "valor": None,
                                    "from": "func"
                                }
                            }
                        else:
                            ids[item[1][2]] = {
                                k: {
                                    "tipo": v,
                                    "valor": None,
                                    "from": "func"
                                }
                            }
                if ids.get(item[1][2]):
                    ids[item[1][2]] |= {
                        "returns": {"tipo": item[1][5] if len(item[1]) == 6 else None}
                    }
                else:
                    ids[item[1][2]] = {
                        "returns": {"tipo": item[1][5] if len(item[1]) == 6 else None}
                    }

                transcript += f"{item[1][2]}:\n"

                if item[2]:
                    t, i = separar_defs([[item[2]]], transcript, item[1][2], ids)
                    transcript = t
                    ids |= i
                t, i = extract_function(ids, transcript, item)
                transcript = t
                ids |= i
                if len(item[4]) > 0:
                    t, i = separar_defs([[item[4]]], transcript, ids_=ids)
                    transcript = t
                    ids |= i

    return transcript, ids


def separar_blocos(arvore):
    blocos = []

    for item in arvore:
        if isinstance(item, tuple) and len(item) > 0 and isinstance(item[0], str) and item[0] == 'BLOCO':
            comandos = item[1] if isinstance(item[1], list) else [item[1]]
            blocos += separar_comandos(comandos)

    return blocos


def separar_comandos(comandos):
    resultado = []

    for comando in comandos:
        if comando is None:
            return []
        if comando[1] == "while":
            _, nome_comando, exp, sub_comandos, sub_bloco = comando
            resultado.append({
                'nome_comando': nome_comando,
                'exp': exp,
                'sub_comandos': sub_comandos,
                'sub_blocos': separar_blocos([sub_bloco])
            })
        elif comando[1] == "if":
            if len(comando) == 6:
                _, nome_comando, exp, sub_comandos, sub_bloco, _else = comando
                resultado.append({
                    'nome_comando': nome_comando,
                    'exp': exp,
                    'sub_comandos': sub_comandos,
                    'sub_blocos': separar_blocos([sub_bloco]),
                    'else': separar_blocos([_else[1]]) if _else else ""
                })
            else:
                _, nome_comando, exp, sub_comandos, sub_bloco = comando
                resultado.append({
                    'nome_comando': nome_comando,
                    'exp': exp,
                    'sub_comandos': sub_comandos,
                    'sub_blocos': separar_blocos([sub_bloco])
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
        
        elif len(comando) == 4:
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
    defs_separadas, ids = separar_defs(arvore, "")
    comandos = separar_blocos(arvore)
    defs_separadas += "\nmain:\n" + extract_comando(comandos, "", "global", ids)

    with open("transcricao_cod_inter.txt", "w") as f:
        f.write(defs_separadas)
