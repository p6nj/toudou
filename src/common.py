from os import environ


def deserialize(var: str):
    if var == "True":
        return True
    elif var == "False":
        return False
    else:
        return var


config = {k[7:]: deserialize(v) for k, v in environ.items() if k.startswith("TOUDOU_")}
