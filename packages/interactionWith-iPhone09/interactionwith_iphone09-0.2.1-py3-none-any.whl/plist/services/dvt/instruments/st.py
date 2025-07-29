from plist.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService


class St:
    IDENTIFIER = 'com.apple.instruments.server.services.screenshot'

    def __init__(self, dvt: DvtSecureSocketProxyService):
        self._channel = dvt.make_channel(self.IDENTIFIER)

    def get_st(self) -> bytes:
        self._channel.takeScreenshot(expects_reply=True)
        return self._channel.receive_plist()
