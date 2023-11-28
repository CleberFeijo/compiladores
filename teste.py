# import json

dict_1 = {
    "num_1": 12,
    "num_2": "13",
    "num_3": 14
}

dict_2 = {}

json_record = {
    "dict_1": {
        "num_1": {"tipo": "int", "valor": None},
        "num_2": {"tipo": "str", "valor": None},
    }
}

array_1 = [12, 12, 14]
array_2 = ["cleber", "luan", "felipe"]
array_3 = []

json_array = {
    "array_1": {
        "tipo": "int",
        "tam": 15,
        "valores": []
    },
    "array_2": {
        "tipo": "str",
        "tam": 15,
        "valores": []
    },
    "array_3": {
        "tipo": "str",
        "tam": 15,
        "valores": []
    }
}


def func(a: int, b: str) -> int:
    c = 2
    try:
        b = int(b)
    except ValueError:
        return Exception("A variável b não pode ser transformada em inteiro.")
    return a + int(b)


json_func = {
    "func": {
        "params": {
            "a": "int",
            "b": "str"
        },
        "returns": "int"
    }
}

var_1 = dict_1
var_2 = 2
var_3 = array_2

json_record = ... #ler json_records

json_var = {
    "var_1": {
        "tipo": "record",
        "valor": "dict_1",
        "estrutura": json_record.get("dict_1").get("valores"),
        "local": "global"
    },
    "var_2": {
        "tipo": "int",
        "valor": 2,
        "estrutura": None,
        "local": "func"
    },
    "var_3": {
        "tipo": "array",
        "valor": "array_2",
        "estrutura": json_array.get("array_2"),
        "local": "global"
    }
}

var_1["num_1"] = 10

type_ = {
    "int": int,
    "str": str,
    "list": list,
    "record": dict,
    "bool": bool,
    "real": float
}

if isinstance(10, type_[json_var["var_1"]["estrutura"]["num_1"]["tipo"]]):
    json_var["var_1"]["estrutura"]["num_1"]["valor"] = 10
else:
    raise ValueError(
        f"Tentativa de atribuir um valor para uma chave do record \
        {json_var['var_1']['valor']} que não é de tipo \
        {type_[json_var['var_1']['estrutura']['num_1']['tipo']]}"
    )

var_2.append("cleber")

if isinstance("cleber", type_[json_var["var_3"]["estrutura"]["tipo"]]):
    json_var["var_3"]["estrutura"]["valores"].append("cleber")
else:
    raise ValueError(
        f"Tentativa de atribuir um valor no array \
        {json_var['var_2']['valor']} que não é de tipo \
        {type_[json_var['var_3']['estrutura']['tipo']]}"
    )
