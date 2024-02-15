from math import inf
from classes.todolist import TodoList
from .main import click
from datetime import datetime
from click import ClickException


@click.group(short_help="make lists or tasks")
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
