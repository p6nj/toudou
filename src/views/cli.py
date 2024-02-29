from math import inf
from classes.todolist import Base
import click
from datetime import datetime
from click import ClickException
from sqlalchemy import create_engine


def main():
    try:
        cli(obj=create_engine("sqlite:///td.db", echo=True))
    except Exception as e:
        print(e)
        exit(0)


@click.group()
@click.pass_context
def cli(ctx):
    """Todo list manager (command-line version)."""
    pass


@cli.command()
@click.pass_context
def init(ctx):
    Base.metadata.create_all(ctx.obj)


@cli.group(short_help="make lists or tasks")
@click.pass_context
def new(ctx):
    """Creates todo lists or tasks."""


@new.command("list", short_help="create a list")
@click.pass_context
@click.argument(
    "name",
    default="default",
    metavar='[LIST="default"]',
)
def newlist(ctx, name):
    """Creates a new list (file) in the current directory."""
    target = TodoList(name, ctx.obj)
    if target.exists():
        raise ClickException("List already exists.")
    target.create()


@new.command("task", short_help="add a task")
@click.pass_context
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
    target = TodoList(list, ctx.obj).pull()
    target.items.append(TodoList.Item(None, task, duefor, False))
    target.push()


@cli.group("del", short_help="delete lists or tasks")
@click.pass_context
def delete(ctx):
    """Deletes todo lists or tasks."""


@delete.command("task", short_help="delete a task")
@click.pass_context
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
    TodoList(list, ctx.obj).nuke_item(task)


@delete.command("list", short_help="delete a list")
@click.pass_context
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
    TodoList(name, ctx.obj).nuke()


@cli.command()
def export():
    pass


@cli.command("import")
def _import():
    pass


@cli.command(short_help="show tasks")
@click.pass_context
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
    print(TodoList(list, ctx).pull())


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
    # TODO
    pass
    # mv(old, new)


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
    # TODO
    pass
    # with open(list, "rb") as file:
    #     todos = load(file)
    # todos.items[id].task = desc
    # with open(list, "wb") as file:
    #     dump(todos, file)


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
    # TODO
    pass
    # with open(list, "rb") as file:
    #     todos = load(file)
    # todos.items[id].done = True
    # with open(list, "wb") as file:
    #     dump(todos, file)


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
    # TODO
    pass
    # with open(list, "rb") as file:
    #     todos = load(file)
    # todos.items[id].done = False
    # with open(list, "wb") as file:
    #     dump(todos, file)
