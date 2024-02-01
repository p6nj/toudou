from os.path import isfile
from os import linesep
import click
from datetime import date
from pickle import dump, load
from dataclasses import dataclass

# alias
l = list


@dataclass
class TodoList:
    @dataclass
    class Todo:
        id: int
        task: str
        date: date | None
        done: bool

        def __str__(self) -> str:
            return (
                "- "
                + self.task
                + (" (" + self.date + ")" if self.date is not None else "")
            )

    # use the next line for multiple todo lists
    # id: ID
    file: str

    def exists(s) -> bool:
        return isfile(s.file)

    def empty(s) -> bool:
        with open(s.file, "br") as file:
            return not file.read()

    def new(s, task: str, date=None):
        if not s.exists:
            with open(s.file, "x+b") as file:
                dump([TodoList.Todo(1, task, date, False)], file)
        else:
            if s.empty:
                with open(s.file, "bw") as file:
                    dump([TodoList.Todo(1, task, date, False)], file)
            else:
                with open(s.file, "br") as file:
                    todolist = load(file)
                with open(s.file, "bw") as file:
                    dump(
                        todolist + [TodoList.Todo(len(todolist), task, date, False)],
                        file,
                    )

    def __str__(s) -> str:
        if not s.exists:
            return "No todolist!"
        if s.empty:
            return "Nothing to do."
        with open(s.file, "br") as file:
            return linesep.join([str(t) for t in load(file)])


@click.group()
def cli():
    pass


@cli.command()
@click.option("-t", "--task", prompt="Your task", help="The task to remember.")
@click.option("-d", "--duefor", help="The date the task is due for.")
def new(task: str, duefor=None):
    TodoList("todolist.p").new(task, duefor)


@cli.command()
def list():
    print(TodoList("todolist.p"))
