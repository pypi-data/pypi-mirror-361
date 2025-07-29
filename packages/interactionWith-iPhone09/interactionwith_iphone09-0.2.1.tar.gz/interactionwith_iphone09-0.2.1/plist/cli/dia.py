import click

from plist.cli.cli_common import Command
from plist.lockdown import LockdownClient
from plist.services.dia import DiaService


@click.group()
def cli() -> None:
    pass


@cli.group()
def dia() -> None:
    pass


@dia.command('restart', cls=Command)
def dia_restart(service_provider: LockdownClient):
    DiaService(lockdown=service_provider).restart()


@dia.command('shutdown', cls=Command)
def dia_shutdown(service_provider: LockdownClient):
    DiaService(lockdown=service_provider).shutdown()

