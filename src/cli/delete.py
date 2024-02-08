from .main import click
from pickle import dump, load
from os import remove


@click.group("del", short_help="delete lists or tasks")
def delete():
    """Deletes todo lists or tasks."""


@delete.command("task", short_help="delete a task")
@click.argument("task", type=int)
@click.option(
    "-l",
    "--list",
    type=click.Path(True, True, readable=True, writable=True),
    default="default",
    help="The todo-list where the task is.",
    metavar='[LIST="default"]',
)
def deltask(task: int, list):
    """Deletes a task from the given list ("default" by default)."""
    with open(list, "rb") as file:
        todos = load(file)
    todos.items.pop(task)
    with open(list, "wb") as file:
        dump(todos, file)


@delete.command("list", short_help="delete a list")
@click.argument(
    "name",
    type=click.Path(True, True, writable=True),
    default="default",
    metavar='[LIST="default"]',
)
def dellist(name):
    """
    Deletes the given list ("default" by default).
    Cannot be undone.
    """
    remove(name)
