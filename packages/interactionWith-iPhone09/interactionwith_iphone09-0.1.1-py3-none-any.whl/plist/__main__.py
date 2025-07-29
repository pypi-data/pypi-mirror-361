import asyncio
import difflib
import logging
import os
import re
import sys
import textwrap
import traceback
from typing import Union

import click
import coloredlogs

from plist.cli.cli_common import TUNNEL_ENV_VAR, isatty
from plist.exceptions import NoDeviceConnectedError, ConnectionFailedError, ConnectionFailedToUsbmuxdError, \
    NotPairedError, UserDeniedPairingError, MessageNotSupportedError, InternalError, AccessDeniedError, \
    TunneldConnectionError, DeviceNotFoundError, InvalidServiceError, RSDRequiredError

from plist.lockdown import retry_create_using_usbmux 
from plist.osu.os_utils import get_os_utils

coloredlogs.install(level=logging.INFO)

logging.getLogger('quic').disabled = True
logging.getLogger('asyncio').disabled = True
logging.getLogger('zeroconf').disabled = True
logging.getLogger('parso.cache').disabled = True
logging.getLogger('parso.cache.pickle').disabled = True
logging.getLogger('parso.python.diff').disabled = True
logging.getLogger('humanfriendly.prompts').disabled = True
logging.getLogger('blib2to3.pgen2.driver').disabled = True
logging.getLogger('urllib3.connectionpool').disabled = True

logger = logging.getLogger(__name__)

INVALID_SERVICE_MESSAGE = "Failed to start service"

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=400)

CLI_GROUPS = {
    'dl': 'dl',
    'dia': 'dia',
    'rt': 'rt',
    'um': 'um',
}

RECONNECT = False


class Pmd3Cli(click.Group):
    def list_commands(self, ctx):
        return CLI_GROUPS.keys()

    def get_command(self, ctx: click.Context, name: str) -> click.Command:
        if name not in CLI_GROUPS.keys():
            self.handle_invalid_command(ctx, name)
        return self.import_and_get_command(ctx, name)

    def handle_invalid_command(self, ctx: click.Context, name: str) -> None:
        suggested_commands = self.search_commands(name)
        suggestion = self.format_suggestions(suggested_commands)
        ctx.fail(f'No such command {name!r}{suggestion}')

    @staticmethod
    def format_suggestions(suggestions: list[str]) -> str:
        if not suggestions:
            return ''
        cmds = textwrap.indent('\n'.join(suggestions), ' ' * 4)
        return f'\nDid you mean this?\n{cmds}'

    @staticmethod
    def import_and_get_command(ctx: click.Context, name: str) -> click.Command:
        module_name = f'plist.cli.{CLI_GROUPS[name]}'
        mod = __import__(module_name, None, None, ['cli'])
        command = mod.cli.get_command(ctx, name)
        if not command:
            command_name = mod.cli.list_commands(ctx)[0]
            command = mod.cli.get_command(ctx, command_name)
        return command

    @staticmethod
    def highlight_keyword(text: str, keyword: str) -> str:
        return re.sub(f'({keyword})', click.style('\\1', bold=True), text, flags=re.IGNORECASE)

    @staticmethod
    def collect_commands(command: click.Command) -> Union[str, list[str]]:
        commands = []
        if isinstance(command, click.Group):
            for k, v in command.commands.items():
                cmd = Pmd3Cli.collect_commands(v)
                if isinstance(cmd, list):
                    commands.extend([f'{command.name} {c}' for c in cmd])
                else:
                    commands.append(f'{command.name} {cmd}')
            return commands
        return f'{command.name}'

    @staticmethod
    def search_commands(pattern: str) -> list[str]:
        all_commands = Pmd3Cli.load_all_commands()
        matched = sorted(filter(lambda cmd: re.search(pattern, cmd), all_commands))
        if not matched:
            matched = difflib.get_close_matches(pattern, all_commands, n=20, cutoff=0.4)
        if isatty():
            matched = [Pmd3Cli.highlight_keyword(cmd, pattern) for cmd in matched]
        return matched

    @staticmethod
    def load_all_commands() -> list[str]:
        all_commands = []
        for key in CLI_GROUPS.keys():
            module_name = f'plist.cli.{CLI_GROUPS[key]}'
            mod = __import__(module_name, None, None, ['cli'])
            cmd = Pmd3Cli.collect_commands(mod.cli.commands[key])
            if isinstance(cmd, list):
                all_commands.extend(cmd)
            else:
                all_commands.append(cmd)
        return all_commands


@click.command(cls=Pmd3Cli, context_settings=CONTEXT_SETTINGS)
@click.option('--reconnect', is_flag=True, default=False, help='Reconnect to device when disconnected.')
def cli(reconnect: bool) -> None:
    global RECONNECT
    RECONNECT = reconnect


def invoke_cli_with_error_handling() -> bool:
    try:
        cli()
    except NoDeviceConnectedError:
        logger.error('Device is not connected')
        return True
    except ConnectionAbortedError:
        logger.error('Device was disconnected')
        return True
    except NotPairedError:
        logger.error('Device is not paired')
    except UserDeniedPairingError:
        logger.error('User refused to trust this computer')

    except MessageNotSupportedError:
        logger.error('Message not supported for this iOS version')
        traceback.print_exc()
    except InternalError:
        logger.error('Internal Error')
    except (InvalidServiceError, RSDRequiredError) as e:
        should_retry_over_tunneld = False
        if isinstance(e, RSDRequiredError):
            logger.warning('Trying again over tunneld since RSD is required for this command')
            should_retry_over_tunneld = True
        elif (e.identifier is not None) and ('dl' in sys.argv) and ('--tunnel' not in sys.argv):
            logger.warning('Got an InvalidServiceError')
            should_retry_over_tunneld = True
        if should_retry_over_tunneld:
            os.environ[TUNNEL_ENV_VAR] = e.identifier or ' '
            return main()
        logger.error(INVALID_SERVICE_MESSAGE)
    except AccessDeniedError:
        logger.error(get_os_utils().access_denied_error)
    except BrokenPipeError:
        traceback.print_exc()
    except TunneldConnectionError:
        logger.error(
            'Unable to connect to Tunneld. You can start one using:\n'
            'sudo python3 -m plist rt tunneld')
    except DeviceNotFoundError as e:
        logger.error(f'Device not found: {e.udid}')
    return False


def main() -> None:
    while invoke_cli_with_error_handling():
        if not RECONNECT:
            break
        try:
            lockdown = retry_create_using_usbmux(None)
            lockdown.close()
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
