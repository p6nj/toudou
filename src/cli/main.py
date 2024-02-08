import click
from .new import new
from .delete import delete
from .show import show


@click.group()
def cli():
    """Todo list manager (command-line version)."""


cli.add_command(new)
cli.add_command(delete)
cli.add_command(show)
