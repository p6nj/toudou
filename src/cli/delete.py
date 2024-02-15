from .main import click
from classes.todolist import TodoList


@click.group("del", short_help="delete lists or tasks")
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
