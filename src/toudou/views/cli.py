from sys import stdin, stdout
from toudou.models import (
    engine,
    List,
    ListNotFoundError,
    Task,
    ListExistsError,
    TaskNotFoundError,
    init as init_db,
)
import click
from datetime import date
from toudou.services.csv import export as exportcsv, _import as importcsv


@click.group()
def cli():
    """Todo list manager (command-line version)."""
    pass


@cli.command()
def init():
    init_db()
    try:
        List("default").create()
    except ListExistsError:
        print("nothing to do.")


@cli.command()
def lists():
    if lists := List.all():
        print("Available lists :")
        for list in lists:
            print("- " + list.name)
    else:
        print('No list available. To create one, use "new list [name]".')


@cli.group(short_help="make lists or tasks")
def new():
    """Creates todo lists or tasks."""


@new.command("list", short_help="create a list")
@click.argument(
    "name",
    default="default",
    metavar='[LIST="default"]',
)
def newlist(name: str):
    """Creates a new list (file) in the current directory."""
    try:
        List(name).create()
    except ListExistsError:
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
def newtask(task: str, list: str, duefor: date = None):
    """Creates a task and add it to the given list ("default" by default)."""
    try:
        Task(desc=task, list=List.read(list), duefor=duefor).create()
    except ListNotFoundError:
        print("List not found.")


@cli.group("del", short_help="delete lists or tasks")
def delete():
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
def deltask(task: int, list: str):
    """Deletes a task from the given list ("default" by default)."""
    try:
        Task.read(list, task).delete()
    except TaskNotFoundError:
        print("Task does not exist.")


@delete.command("list", short_help="delete a list")
@click.argument(
    "name",
    default="default",
    metavar='[LIST="default"]',
)
def dellist(name: str):
    """
    Deletes the given list ("default" by default).
    Cannot be undone.
    """
    try:
        List.read(name).delete()
    except ListNotFoundError:
        print(f'"{name}" list does not exist.')


@cli.command(short_help="show tasks")
@click.argument(
    "list",
    default="default",
    metavar='[LIST="default"]',
)
def show(list: str):
    """
    Shows tasks from a list.
    If no list name is given, show "default" tasks.
    """
    try:
        print(List.read(list))
    except ListNotFoundError:
        print(f'"{list}" list does not exist.')


@cli.group()
def rename():
    pass


@rename.command("list")
@click.argument("old")
@click.argument("new")
def updatelist(old: str, new: str):
    try:
        List(old).update(new)
    except ListNotFoundError:
        print(f'"{old}" list does not exist.')


@rename.command("task")
@click.argument("id", type=int)
@click.argument("desc")
@click.option(
    "-l",
    "--list",
    default="default",
    metavar='[LIST="default"]',
)
def updatetaskdesc(id: int, desc: str, list: str):
    try:
        Task.read(id, list).update(desc=desc)
    except TaskNotFoundError:
        print(f'"{list}" list does not exist.')


@cli.command("do")
@click.argument("id", type=int)
@click.option(
    "-l",
    "--list",
    default="default",
    metavar='[LIST="default"]',
)
def markdone(id: int, list: str):
    try:
        Task.read(id, list).update(newdone=True)
    except TaskNotFoundError:
        print("Task does not exist.")


@cli.command("undo")
@click.argument("id", type=int)
@click.option(
    "-l",
    "--list",
    default="default",
    metavar='[LIST="default"]',
)
def markundone(id: int, list: str):
    try:
        Task.read(id, list).update(newdone=False)
    except TaskNotFoundError:
        print("Task does not exist.")


@cli.command("export")
# got this trick from https://stackoverflow.com/a/59830073
@click.argument("file", default=stdout, metavar="[FILE=stdout]", type=click.File("w"))
def csvexport(file):
    """Export as CSV to stdout or to a file."""
    file.write(exportcsv())


@cli.command("import")
@click.argument("file", default=stdin, metavar="[FILE=stdin]", type=click.File("r"))
def csvimport(file):
    """Import as CSV from stdin or from a file."""
    importcsv("".join(file.readlines()[1:]))
