from plist.exceptions import ConnectionFailedError
from plist.lockdown import LockdownClient
from plist.lockdown_service_provider import LockdownServiceProvider
from plist.services.lockdown_service import LockdownService

class DiaService(LockdownService):
    RSD_SERVICE_NAME = 'com.apple.mobile.dia_relay.shim.remote'
    SERVICE_NAME = 'com.apple.mobile.diagnostics_relay'
    OLD_SERVICE_NAME = 'com.apple.iosdia.relay'

    def __init__(self, lockdown: LockdownServiceProvider):
        if isinstance(lockdown, LockdownClient):
            try:
                service = lockdown.start_lockdown_service(self.SERVICE_NAME)
                service_name = self.SERVICE_NAME
            except ConnectionFailedError:
                service = lockdown.start_lockdown_service(self.OLD_SERVICE_NAME)
                service_name = self.OLD_SERVICE_NAME
        else:
            service = None
            service_name = self.RSD_SERVICE_NAME
        super().__init__(lockdown, service_name, service=service)
    def action(self, action: str):
        response = self.service.send_recv_plist({'Request': action})
        #if response['Status'] != 'Success':
        #    raise PlistException(f'failed to perform action: {action}')
        response.get('Dia')

    def restart(self):
        self.action('Restart')

    def shutdown(self):
        self.action('Shutdown')
