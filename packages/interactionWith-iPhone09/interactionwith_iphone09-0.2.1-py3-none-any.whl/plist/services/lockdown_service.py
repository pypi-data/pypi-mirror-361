import logging

from plist.lockdown_service_provider import LockdownServiceProvider
from plist.service_connection import ServiceConnection


class LockdownService:
    def __init__(self, lockdown: LockdownServiceProvider, service_name: str, is_developer_service=False,
                 service: ServiceConnection = None, include_escrow_bag: bool = False):

        if service is None:
            start_service = lockdown.start_lockdown_developer_service if is_developer_service else \
                lockdown.start_lockdown_service
            service = start_service(service_name, include_escrow_bag=include_escrow_bag)

        self.service_name = service_name
        self.lockdown = lockdown
        self.service = service
        self.logger = logging.getLogger(self.__module__)

    def __enter__(self):
        return self

    async def __aenter__(self) -> 'LockdownService':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.service.aio_close()

    def close(self) -> None:
        self.service.close()
