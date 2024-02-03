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
    pass


@cli.group()
def new():
    pass


@cli.group("del")
def delete():
    pass


@cli.command()
@click.argument(
    "list",
    type=click.File("rb"),
    default="default",
)
def show(list):
    print(load(list))


@new.command("list")
@click.argument(
    "name",
    type=click.File("xb"),
    default="default",
)
def newlist(name):
    dump(TodoList(), name)


@new.command("task")
@click.argument("task")
@click.option(
    "-l",
    "--list",
    type=click.Path(True, True, readable=True, writable=True),
    default="default",
    help="The todo-list where to put this task.",
)
@click.option("-d", "--duefor", help="The date the task is due for.")
def newtask(task: str, list, duefor=None):
    with open(list, "rb") as file:
        todos = load(file)
    todos.items.append(TodoList.Item(task, duefor, False))
    with open(list, "wb") as file:
        dump(todos, file)


@delete.command("task")
@click.argument("task", type=int)
@click.option(
    "-l",
    "--list",
    type=click.Path(True, True, readable=True, writable=True),
    default="default",
    help="The todo-list where to put this task.",
)
def deltask(task: int, list):
    with open(list, "rb") as file:
        todos = load(file)
    todos.items.pop(task)
    with open(list, "wb") as file:
        dump(todos, file)


@delete.command("list")
@click.argument(
    "name",
    type=click.Path(True, True, writable=True),
    default="default",
)
def dellist(name):
    remove(name)
