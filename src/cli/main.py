import click
from .create import new
from .delete import delete
from .read import show
from .update import rename, markdone, markundone


@click.group()
def cli():
    """Todo list manager (command-line version)."""


cli.add_command(new)
cli.add_command(delete)
cli.add_command(show)
cli.add_command(rename)
cli.add_command(markdone)
cli.add_command(markundone)
