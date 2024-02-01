from os.path import isfile
import click
import uuid
from datetime import date
from pickle import dump, load
from dataclasses import dataclass

# alias
l = list

# globals
TODOLIST = "todolist.p"


@dataclass
class Todo:
    id: uuid.UUID
    task: str
    date: date | None
    done: bool

    def __str__(self) -> str:
        return (
            "I need to "
            + self.task
            + ("for " + self.date if self.date is not None else "")
        )


@click.group()
def cli():
    pass


@cli.command()
@click.option("-t", "--task", prompt="Your task", help="The task to remember.")
@click.option("-d", "--duefor", help="The date the task is due for.")
def new(task: str, duefor=None):
    todo = Todo(uuid.uuid4(), task, duefor, False)
    if not isfile(TODOLIST):
        print("new todolist")
        with open(TODOLIST, "x+b") as file:
            dump([todo], file)
    else:
        with open(TODOLIST, "br") as file:
            empty = not file.read()
        if empty:
            print("that's the only task in the list")
            with open(TODOLIST, "bw") as file:
                dump([todo], file)
        else:
            with open(TODOLIST, "br") as file:
                todolist = load(file)
            with open(TODOLIST, "bw") as file:
                dump(todolist + [todo], file)


@cli.command()
def list():
    with open(TODOLIST, "br") as file:
        for todo in load(file):
            print(todo)
