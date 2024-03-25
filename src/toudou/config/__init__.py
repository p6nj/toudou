from os import environ

config = {
    k[7:]: True if v == "True" else False if v == "False" else v
    for k, v in environ.items()
    if k.startswith("TOUDOU_")
}
