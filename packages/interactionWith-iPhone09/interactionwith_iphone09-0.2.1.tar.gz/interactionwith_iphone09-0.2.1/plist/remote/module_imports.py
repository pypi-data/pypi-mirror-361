import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

try:
    from plist.remote.tunnel_service import RemotePairingQuicTunnel, start_tunnel

    MAX_IDLE_TIMEOUT = RemotePairingQuicTunnel.MAX_IDLE_TIMEOUT
except ImportError:
    start_tunnel: Optional[Callable] = None
    MAX_IDLE_TIMEOUT = None

GENERAL_IMPORT_ERROR = "Failed"


def verify_tunnel_imports() -> bool:
    if start_tunnel is not None:
        return True
    logger.error(GENERAL_IMPORT_ERROR)
    return False
