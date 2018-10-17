import click
from quart.cli import QuartGroup

from charge.app import create_app


def create_charge(info):
    return create_app(cli=True)


@click.group(cls=QuartGroup, create_app=create_charge)
def cli():
    """Main entry point"""


@cli.command("init")
def init():
    """Init application, create database tables
    and create a new user named admin with password admin
    """
    from charge.extensions import db

    click.echo("create database")
    db.create_all()
    click.echo("done")


if __name__ == "__main__":
    cli()
