import json


def get_info(name: str, type_: str) -> dict:
    """
    Acessa o json relacionado à variável 'type_' e puxa as informações
    referentes ao nome enviado nos parâmetros.

    :params:
        - name: str: Nome da função, lista ou dict, salvo como chave do json.
        - type_: str: Tipo que serve de referência para qual json buscar.

    :returns: dict: Dicionário com as informações da função, lista ou dict.
    """
    name_json = {
        "func": "json_func.json",
        "array": "json_array.json",
        "record": "json_record.json",
        "const": "json_const.json",
        "var": "json_var.json"
    }
    with open(name_json[type_], "r") as js:
        dados = json.load(js)
        js.close()
    for dado in dados:
        if dado["nome"] == name:
            return dado
