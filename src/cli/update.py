from .main import click
from os import rename as mv
from pickle import load, dump


@click.group()
def rename():
    pass


@rename.command("list")
@click.argument(
    "old",
    type=click.Path(True, True, writable=True),
)
@click.argument("new", type=click.Path(False))
def updatelist(old: str, new: str):
    mv(old, new)


@rename.command("task")
@click.argument("id", type=int)
@click.argument("desc")
@click.option(
    "-l",
    "--list",
    type=click.Path(True, True, readable=True, writable=True),
    default="default",
    help="The todo-list where to put this task.",
    metavar='[LIST="default"]',
)
def updatetaskdesc(id: int, desc: str, list: str):
    with open(list, "rb") as file:
        todos = load(file)
    todos.items[id].task = desc
    with open(list, "wb") as file:
        dump(todos, file)
