from os.path import isfile
from os import linesep
import click
from datetime import date
from pickle import dump, load
from dataclasses import dataclass

# alias
l = list


class TodoList:
    def __init__(self) -> None:
        self.items: [TodoList.Item] = []

    def __str__(self) -> str:
        return linesep.join([str(t) for t in self.items])

    @dataclass
    class Item:
        task: str
        date: date | None
        done: bool

        def __str__(self) -> str:
            return (
                "- "
                + self.task
                + (" (" + self.date + ")" if self.date is not None else "")
            )


@click.group()
def cli():
    pass


@cli.group()
def lists():
    pass


@cli.group()
def new():
    pass


@new.command()
@click.argument("name", type=click.File("xb"))
def list(name):
    dump(TodoList(), name)


@new.command()
@click.argument("task")
@click.option(
    "-l",
    "--list",
    type=click.File("rb+"),
    prompt="Todo-list",
    help="The todo-list where to put this task.",
)
@click.option("-d", "--duefor", help="The date the task is due for.")
def todo(task: str, list, duefor=None):
    todos = load(list)
    todos.items.append(TodoList.Item(task, duefor, False))
    dump(todos, list)
