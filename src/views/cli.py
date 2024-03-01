from math import inf
from models.todolist import (
    Base,
    List,
    ListNotFoundError,
    Task,
    ListExistsError,
    TaskNotFoundError,
)
import click
from datetime import datetime
from click import ClickException
from sqlalchemy import create_engine


@click.group()
def cli(ctx):
    """Todo list manager (command-line version)."""
    pass


@cli.command()
def init(ctx):
    Base.metadata.create_all(ctx.obj)


@cli.group(short_help="make lists or tasks")
def new(ctx):
    """Creates todo lists or tasks."""


@new.command("list", short_help="create a list")
@click.argument(
    "name",
    default="default",
    metavar='[LIST="default"]',
)
def newlist(ctx, name: str):
    """Creates a new list (file) in the current directory."""
    try:
        List.create(name)
    except ListExistsError as e:
        print(f'"{name}" list already exists.')


@new.command("task", short_help="add a task")
@click.argument("task")
@click.option(
    "-l",
    "--list",
    default="default",
    help="The todo-list where to put this task.",
    metavar='[LIST="default"]',
)
@click.option(
    "-d",
    "--duefor",
    type=click.DateTime(["%d/%m"]),
    help="The date this task is due for.",
)
@click.option("-d", "--duefor", help="The date the task is due for.")
def newtask(ctx, task: str, list: str, duefor: datetime = None):
    """Creates a task and add it to the given list ("default" by default)."""
    Task.create(task, list, duefor)


@cli.group("del", short_help="delete lists or tasks")
def delete(ctx):
    """Deletes todo lists or tasks."""


@delete.command("task", short_help="delete a task")
@click.argument("task", type=int)
@click.option(
    "-l",
    "--list",
    default="default",
    help="The todo-list where the task is.",
    metavar='[LIST="default"]',
)
def deltask(ctx, task: int, list: str):
    """Deletes a task from the given list ("default" by default)."""
    try:
        Task.delete(list, task)
    except TaskNotFoundError:
        print("Task does not exist.")


@delete.command("list", short_help="delete a list")
@click.argument(
    "name",
    default="default",
    metavar='[LIST="default"]',
)
def dellist(ctx, name: str):
    """
    Deletes the given list ("default" by default).
    Cannot be undone.
    """
    try:
        List.delete(name)
    except ListNotFoundError:
        print("List does not exist.")


@cli.command()
def export():
    pass


@cli.command("import")
def _import():
    pass


@cli.command(short_help="show tasks")
@click.argument(
    "list",
    default="default",
    metavar='[LIST="default"]',
)
def show(ctx, list: str):
    """
    Shows tasks from a list.
    If no list name is given, show "default" tasks.
    """
    try:
        print(List.read(list))
    except ListNotFoundError:
        print("List does not exist.")


@cli.group()
def rename():
    pass


@rename.command("list")
@click.argument(
    "old",
    type=click.Path(True, True, writable=True),
)
@click.argument("new", type=click.Path(False))
def updatelist(old: str, new: str):
    try:
        List.update(old, new)
    except ListNotFoundError:
        print("List does not exist.")


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
    try:
        Task.update(list, id, desc)
    except TaskNotFoundError:
        print("Task does not exist.")


@click.command("do")
@click.argument("id", type=int)
@click.option(
    "-l",
    "--list",
    type=click.Path(True, True, readable=True, writable=True),
    default="default",
    help="The todo-list where to put this task.",
    metavar='[LIST="default"]',
)
def markdone(id: int, list: str):
    try:
        Task.update(list, id, newdone=True)
    except TaskNotFoundError:
        print("Task does not exist.")


@click.command("undo")
@click.argument("id", type=int)
@click.option(
    "-l",
    "--list",
    type=click.Path(True, True, readable=True, writable=True),
    default="default",
    help="The todo-list where to put this task.",
    metavar='[LIST="default"]',
)
def markundone(id: int, list: str):
    try:
        Task.update(list, id, newdone=False)
    except TaskNotFoundError:
        print("Task does not exist.")
