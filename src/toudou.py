from os import linesep, remove
import click
from datetime import date
from pickle import dump, load
from dataclasses import dataclass


class TodoList:
    def __init__(self) -> None:
        self.items: [TodoList.Item] = []

    def __str__(self) -> str:
        return (
            linesep.join([f"{i}\t{t}" for i, t in enumerate(self.items)])
            if self.items
            else "The problem with doing nothing is not knowing when you're finished."
            + linesep
            + "\t\t-- Benjamin Franklin"
        )

    @dataclass
    class Item:
        task: str
        date: date | None
        done: bool

        def __str__(self) -> str:
            return self.task + (" (" + self.date + ")" if self.date is not None else "")


@click.group()
def cli():
    """Todo list manager (command-line version)."""


@cli.group(short_help="make lists or tasks")
def new():
    """Creates todo lists or tasks."""


@cli.group("del", short_help="delete lists or tasks")
def delete():
    """Deletes todo lists or tasks."""


@cli.command(short_help="show tasks")
@click.argument(
    "list", type=click.File("rb"), default="default", metavar='[LIST="default"]'
)
def show(list):
    """
    Shows tasks from a list.
    If no list name is given, show "default" tasks.
    """
    print(load(list))


@new.command("list", short_help="create a list")
@click.argument(
    "name",
    type=click.File("xb"),
    default="default",
    metavar='[LIST="default"]',
)
def newlist(name):
    """Creates a new list (file) in the current directory."""
    dump(TodoList(), name)


@new.command("task", short_help="add a task")
@click.argument("task")
@click.option(
    "-l",
    "--list",
    type=click.Path(True, True, readable=True, writable=True),
    default="default",
    help="The todo-list where to put this task.",
    metavar='[LIST="default"]',
)
@click.option("-d", "--duefor", help="The date the task is due for.")
def newtask(task: str, list, duefor=None):
    """Creates a task and add it to the given list ("default" by default)."""
    with open(list, "rb") as file:
        todos = load(file)
    todos.items.append(TodoList.Item(task, duefor, False))
    with open(list, "wb") as file:
        dump(todos, file)


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
