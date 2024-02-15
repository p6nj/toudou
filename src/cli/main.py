import click
from .create import new
from .delete import delete
from .read import show
from .update import rename, markdone, markundone
from sqlite3 import connect


def main():
    cli(obj=connect("td.db").cursor())


@click.group()
@click.pass_context
def cli(ctx):
    """Todo list manager (command-line version)."""
    ctx.obj.executescript(open("td.sql", "r").read())


cli.add_command(new)
cli.add_command(delete)
cli.add_command(show)
cli.add_command(rename)
cli.add_command(markdone)
cli.add_command(markundone)
