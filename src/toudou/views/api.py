from flask import Blueprint
from toudou.models import List, ListNotFoundError


api = Blueprint(
    "api",
    __name__,
    url_prefix="/",
    static_url_path="../static",
    template_folder="../templates",
)


@api.get("/lists")
def getlists():
    return {list.name: dict(list) for list in List.all()}


@api.get("/list/<name>")
def getlist(name: str):
    try:
        return dict(List.read(name))
    except ListNotFoundError:
        return "List not found", 400
