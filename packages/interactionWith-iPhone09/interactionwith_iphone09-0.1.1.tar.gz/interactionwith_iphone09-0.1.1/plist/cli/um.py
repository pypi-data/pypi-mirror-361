import logging
import tempfile

import click

from plist import usbmux
from plist.cli.cli_common import USBMUX_OPTION_HELP, BaseCommand, print_json
from plist.lockdown import create_using_usbmux
from plist.tcp_forwarder import UsbmuxTcpForwarder

logger = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    pass


@cli.group('um')
def um() -> None:
    pass


@um.command('forward', cls=BaseCommand)
@click.option('usbmux_address', '--usbmux', help=USBMUX_OPTION_HELP)
@click.argument('src_port', type=click.IntRange(1, 0xffff))
@click.argument('dst_port', type=click.IntRange(1, 0xffff))

def usbmux_forward(usbmux_address: str, src_port: int, dst_port: int, serial: str, daemonize: bool):
    forwarder = UsbmuxTcpForwarder(serial, dst_port, src_port, usbmux_address=usbmux_address)

    if daemonize:
        try:
            from daemonize import Daemonize
        except ImportError:
            raise NotImplementedError('daemonizing is only supported on unix platforms')

        with tempfile.NamedTemporaryFile('wt') as pid_file:
            daemon = Daemonize(app=f'forwarder {src_port}->{dst_port}', pid=pid_file.name, action=forwarder.start)
            daemon.start()
    else:
        forwarder.start()


@um.command('list', cls=BaseCommand)
@click.option('usbmux_address', '--usbmux', help=USBMUX_OPTION_HELP)
@click.option('-u', '--usb', is_flag=True, help='show only usb devices')
@click.option('-n', '--network', is_flag=True, help='show only network devices')
def usbmux_list(usbmux_address: str, usb: bool, network: bool) -> None:
    connected_devices = []
    for device in usbmux.list_devices(usbmux_address=usbmux_address):
        udid = device.serial

        if usb and not device.is_usb:
            continue

        if network and not device.is_network:
            continue

        lockdown = create_using_usbmux(udid, autopair=False, connection_type=device.connection_type,
                                       usbmux_address=usbmux_address)
        connected_devices.append(lockdown.short_info)

    print_json(connected_devices)
