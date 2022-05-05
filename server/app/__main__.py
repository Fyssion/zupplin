from __future__ import annotations

import asyncio
import traceback

import click
import toml

from .app import Application
from .utils.database import Database, DROP_TABLES


def load_config():
    with open("config.toml", "r") as f:
        return toml.load(f)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context):
    if ctx.invoked_subcommand is None:
        config = load_config()
        Application.run(config)


@cli.group()
def db():
    pass


@db.command()
def drop():
    config = load_config()

    try:
        db = asyncio.run(Database.connect(config['database']))
    except Exception:
        click.echo(
            f"Could not connect to the database.\n{traceback.format_exc()}",
            err=True,
        )
        return

    click.confirm("Are you sure you want to drop all tables in the database? This action cannot be undone.", abort=True)

    try:
        asyncio.run(db.pool.execute(DROP_TABLES))
    except Exception:
        click.echo(
            f"Could not drop the database.\n{traceback.format_exc()}",
            err=True,
        )
        return

    click.echo("Dropped all tables in the database.")


cli()
