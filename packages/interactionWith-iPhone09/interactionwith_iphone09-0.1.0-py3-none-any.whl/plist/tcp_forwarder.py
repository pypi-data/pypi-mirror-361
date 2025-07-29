import logging
import select
import socket
import threading
import time
from abc import abstractmethod
from typing import Optional

from plist import usbmux
from plist.exceptions import ConnectionFailedError
from plist.lockdown_service_provider import LockdownServiceProvider


class TcpForwarderBase:

    MAX_FORWARDED_CONNECTIONS = 200
    TIMEOUT = 1

    def __init__(self, src_port: int, listening_event: threading.Event = None):
        self.logger = logging.getLogger(__name__)
        self.src_port = src_port
        self.server_socket = None
        self.inputs = []
        self.stopped = threading.Event()
        self.listening_event = listening_event

        self.connections = {}

    def start(self, address='0.0.0.0'):
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((address, self.src_port))
        self.server_socket.listen(self.MAX_FORWARDED_CONNECTIONS)
        self.server_socket.setblocking(False)

        self.inputs = [self.server_socket]
        if self.listening_event:
            self.listening_event.set()

        while self.inputs:
            readable, writable, exceptional = select.select(self.inputs, [], self.inputs, self.TIMEOUT)
            if self.stopped.is_set():
                self.logger.debug("Closing since stopped is set")
                break

            closed_sockets = set()
            for current_sock in readable:
                self.logger.debug("Processing %r", current_sock)
                if current_sock is self.server_socket:
                    self._handle_server_connection()
                else:
                    if current_sock not in closed_sockets:
                        try:
                            self._handle_data(current_sock, closed_sockets)
                        except ConnectionResetError:
                            self.logger.exception("Error when handling data")
                            self._handle_close_or_error(current_sock)
                    else:
                        self.logger.debug("Is closed")

            for current_sock in exceptional:
                self.logger.error("Sock failed: %r", current_sock)
                self._handle_close_or_error(current_sock)

        self.logger.info("Closing everything")
        for current_sock in self.inputs:
            current_sock.close()

    def _handle_close_or_error(self, from_sock):
        other_sock = self.connections[from_sock]

        other_sock.close()
        from_sock.close()
        self.inputs.remove(other_sock)
        self.inputs.remove(from_sock)

        self.logger.info(f'connection {other_sock} was closed')

    def _handle_data(self, from_sock, closed_sockets):
        self.logger.debug(f"Handling data from {from_sock}")
        try:
            data = from_sock.recv(1024)
            if not data:
                raise ConnectionResetError("Connection closed by the peer.")
        except BlockingIOError:
            self.logger.warning(f"Non-blocking read failed on {from_sock}, retrying later.")
            return
        except OSError as e:
            self.logger.error(f"Error reading from socket {from_sock}: {e}")
            self._handle_close_or_error(from_sock)
            closed_sockets.add(from_sock)
            return

        other_sock = self.connections.get(from_sock)
        if not other_sock:
            self.logger.error(f"No connection mapping found for {from_sock}.")
            return

        try:
            total_sent = 0
            while total_sent < len(data):
                try:
                    sent = other_sock.send(data[total_sent:])
                    total_sent += sent
                except BlockingIOError:
                    self.logger.warning(f"Socket buffer full for {other_sock}, retrying in 100ms.")
                    time.sleep(0.1)  # Introduce a small delay
                except BrokenPipeError:
                    self.logger.error(f"Broken pipe error on {other_sock}.")
                    raise
        except OSError as e:
            self.logger.error(f"Unhandled error while forwarding data: {e}")
            self._handle_close_or_error(from_sock)
            closed_sockets.add(from_sock)
            closed_sockets.add(other_sock)

    @abstractmethod
    def _establish_remote_connection(self) -> socket.socket:
        pass

    def _handle_server_connection(self):
        local_connection, client_address = self.server_socket.accept()
        local_connection.setblocking(False)

        try:
            remote_connection = self._establish_remote_connection()
        except ConnectionFailedError:
            self.logger.error(f'failed to connect to port: {self.dst_port}')
            local_connection.close()
            return

        remote_connection.setblocking(False)

        self.inputs.append(local_connection)
        self.inputs.append(remote_connection)

        self.connections[remote_connection] = local_connection
        self.connections[local_connection] = remote_connection

        self.logger.info('connection established from local to remote')

    def stop(self):
        self.stopped.set()


class UsbmuxTcpForwarder(TcpForwarderBase):

    def __init__(self, serial: str, dst_port: int, src_port: int, listening_event: threading.Event = None,
                 usbmux_connection_type: str = None, usbmux_address: Optional[str] = None):
        super().__init__(src_port, listening_event)
        self.serial = serial
        self.dst_port = dst_port
        self.usbmux_connection_type = usbmux_connection_type
        self.usbmux_address = usbmux_address

    def _establish_remote_connection(self) -> socket.socket:
        # connect directly using usbmuxd
        mux_device = usbmux.select_device(self.serial, connection_type=self.usbmux_connection_type,
                                          usbmux_address=self.usbmux_address)
        self.logger.debug("Selected device: %r", mux_device)
        if mux_device is None:
            raise ConnectionFailedError()
        return mux_device.connect(self.dst_port, usbmux_address=self.usbmux_address)


class LockdownTcpForwarder(TcpForwarderBase):

    def __init__(self, service_provider: LockdownServiceProvider, src_port: int, service_name: str,
                 listening_event: threading.Event = None):
        super().__init__(src_port, listening_event)
        self.service_provider = service_provider
        self.service_name = service_name

    def _establish_remote_connection(self) -> socket.socket:
        return self.service_provider.start_lockdown_developer_service(self.service_name).socket
