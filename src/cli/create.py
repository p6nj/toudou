from .main import click
from pickle import load, dump
from classes.todolist import TodoList
from datetime import datetime


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
    ctx.obj.execute(f"insert into list values ('{name}')")
    ctx.obj.connection.commit()


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
@click.option(
    "-d",
    "--duefor",
    type=click.DateTime(["%d/%m"]),
    help="The date this task is due for.",
)
@click.option("-d", "--duefor", help="The date the task is due for.")
def newtask(task: str, list: str, duefor: datetime = None):
    """Creates a task and add it to the given list ("default" by default)."""
    with open(list, "rb") as file:
        todos = load(file)
    todos.items.append(TodoList.Item(task, duefor.date(), False))
    with open(list, "wb") as file:
        dump(todos, file)