import asyncio
import json
import logging
import os
import posixpath
import shlex
import signal
import sys
import time
from collections import namedtuple
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import IO, Optional

import click
from click.exceptions import MissingParameter, UsageError
from packaging.version import Version
from pykdebugparser.pykdebugparser import PyKdebugParser

import plist
from plist.cli.cli_common import BASED_INT, Command, RSDCommand, default_json_encoder, print_json, \
    user_requested_colored_output
from plist.exceptions import CoreDeviceError, DeviceAlreadyInUseError, DvtDirListError, \
    ExtractingStackshotError, RSDRequiredError, UnrecognizedSelectorError
from plist.lockdown import LockdownClient, create_using_usbmux
from plist.osu.os_utils import get_os_utils
from plist.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService
from plist.services.dvt.instruments.device_info import DeviceInfo
from plist.services.dvt.instruments.st import St
from plist.services.st import StS

OSUTILS = get_os_utils()
BSC_SUBCLASS = 0x40c
BSC_CLASS = 0x4
VFS_AND_TRACES_SET = {0x03010000, 0x07ff0000}
DEBUGSERVER_CONNECTION_STEPS = ""

MatchedProcessByPid = namedtuple('MatchedProcess', 'name pid')

logger = logging.getLogger(__name__)

@click.group()
def cli() -> None:
    pass


@cli.group()
def developer() -> None:
    pass

@developer.group()
def dvt() -> None:
    pass

@dvt.command('di', cls=Command)
def di(service_provider: LockdownClient):
    with DvtSecureSocketProxyService(lockdown=service_provider) as dvt:
        device_info = DeviceInfo(dvt)
        info = {
            'hardware': device_info.hardware_information(),
            'network': device_info.network_information(),
            'kernel-name': device_info.mach_kernel_name(),
            'kpep-database': device_info.kpep_database(),
        }
        try:
            info['system'] = device_info.system_information()
        except UnrecognizedSelectorError:
            pass
        print_json(info)

@dvt.command('s', cls=Command)
@click.argument('out', type=click.File('wb'))
def sh(service_provider: LockdownClient, out):
    with DvtSecureSocketProxyService(lockdown=service_provider) as dvt:
        out.write(St(dvt).get_st())
