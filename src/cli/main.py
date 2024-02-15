import click
from .create import new
from .delete import delete
from .read import show
from .update import rename, markdone, markundone
from sqlite3 import connect


@click.group()
@click.pass_context
def cli(ctx):
    """Todo list manager (command-line version)."""
    ctx.con = connect("toudou.db").cursor()
    ctx.con.executescript(open("toudou.sql", "r").read())


cli.add_command(new)
cli.add_command(delete)
cli.add_command(show)
cli.add_command(rename)
cli.add_command(markdone)
cli.add_command(markundone)
