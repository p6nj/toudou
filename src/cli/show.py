from .main import click
from pickle import load


@click.command(short_help="show tasks")
@click.argument(
    "list", type=click.File("rb"), default="default", metavar='[LIST="default"]'
)
def show(list):
    """
    Shows tasks from a list.
    If no list name is given, show "default" tasks.
    """
    print(load(list))
