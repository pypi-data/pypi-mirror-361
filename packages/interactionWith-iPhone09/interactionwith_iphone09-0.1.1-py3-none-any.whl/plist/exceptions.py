__all__ = [
    'PlistException', 'DeviceVersionNotSupportedError', 'IncorrectModeError',
    'NotTrustedError', 'PairingError', 'NotPairedError', 'CannotStopSessionError',
    'PasswordRequiredError', 'StartServiceError', 'FatalPairingError', 'NoDeviceConnectedError', 'DeviceNotFoundError',
    'TunneldConnectionError', 'ConnectionFailedToUsbmuxdError', 'MuxException', 'InvalidConnectionError',
    'MuxVersionError', 'ArgumentError', 'AfcException', 'AfcFileNotFoundError', 'DvtException', 'DvtDirListError',
    'NotMountedError', 'AlreadyMountedError', 'UnsupportedCommandError', 'ExtractingStackshotError',
    'ConnectionTerminatedError', 'WirError', 'WebInspectorNotEnabledError', 'RemoteAutomationNotEnabledError',
    'ArbitrationError', 'InternalError', 'DeveloperModeIsNotEnabledError', 'DeviceAlreadyInUseError', 'LockdownError',
    'PairingDialogResponsePendingError', 'UserDeniedPairingError', 'InvalidHostIDError', 'SetProhibitedError',
    'MissingValueError', 'PasscodeRequiredError', 'AmfiError', 'DeviceHasPasscodeSetError', 'NotificationTimeoutError',
    'DeveloperModeError', 'ProfileError', 'IRecvError', 'IRecvNoDeviceConnectedError', 'UnrecognizedSelectorError',
    'MessageNotSupportedError', 'InvalidServiceError', 'InspectorEvaluateError',
    'LaunchingApplicationError', 'BadCommandError', 'BadDevError', 'ConnectionFailedError', 'CoreDeviceError',
    'AccessDeniedError', 'RSDRequiredError', 'SysdiagnoseTimeoutError', 'GetProhibitedError',
    'FeatureNotSupportedError', 'OSNotSupportedError', 'DeprecationError', 'NotEnoughDiskSpaceError',
    'CloudConfigurationAlreadyPresentError', 'QuicProtocolNotSupportedError', 'RemotePairingCompletedError',
    'DisableMemoryLimitError',
]

from typing import Optional


class PlistException(Exception):
    pass


class DeviceVersionNotSupportedError(PlistException):
    pass


class IncorrectModeError(PlistException):
    pass


class NotTrustedError(PlistException):
    pass


class PairingError(PlistException):
    pass


class NotPairedError(PlistException):
    pass


class CannotStopSessionError(PlistException):
    pass


class PasswordRequiredError(PairingError):
    pass


class StartServiceError(PlistException):
    pass


class FatalPairingError(PlistException):
    pass


class NoDeviceConnectedError(PlistException):
    pass


class InterfaceIndexNotFoundError(PlistException):
    def __init__(self, address: str):
        super().__init__()
        self.address = address


class DeviceNotFoundError(PlistException):
    def __init__(self, udid: str):
        super().__init__()
        self.udid = udid


class TunneldConnectionError(PlistException):
    pass


class MuxException(PlistException):
    pass


class MuxVersionError(MuxException):
    pass


class BadCommandError(MuxException):
    pass


class BadDevError(MuxException):
    pass


class ConnectionFailedError(MuxException):
    pass


class ConnectionFailedToUsbmuxdError(ConnectionFailedError):
    pass


class ArgumentError(PlistException):
    pass


class AfcException(PlistException, OSError):
    def __init__(self, message, status):
        OSError.__init__(self, status, message)
        self.status = status


class AfcFileNotFoundError(AfcException):
    pass


class DvtException(PlistException):
    pass


class UnrecognizedSelectorError(DvtException):
    pass


class DvtDirListError(DvtException):
    pass


class NotMountedError(PlistException):
    pass


class AlreadyMountedError(PlistException):
    pass


class MissingManifestError(PlistException):
    pass


class UnsupportedCommandError(PlistException):
    pass


class ExtractingStackshotError(PlistException):
    pass


class ConnectionTerminatedError(PlistException):
    pass


class StreamClosedError(ConnectionTerminatedError):
    pass


class WebInspectorNotEnabledError(PlistException):
    pass


class RemoteAutomationNotEnabledError(PlistException):
    pass


class WirError(PlistException):
    pass


class InternalError(PlistException):
    pass


class ArbitrationError(PlistException):
    pass


class DeviceAlreadyInUseError(ArbitrationError):

    @property
    def message(self):
        return self.args[0].get('message')

    @property
    def owner(self):
        return self.args[0].get('owner')

    @property
    def result(self):
        return self.args[0].get('result')


class DeveloperModeIsNotEnabledError(PlistException):
    pass


class DeveloperDiskImageNotFoundError(PlistException):
    pass


class DeveloperModeError(PlistException):
    pass


class LockdownError(PlistException):

    def __init__(self, message: str, identifier: Optional[str] = None) -> None:
        super().__init__(message)
        self.identifier = identifier


class GetProhibitedError(LockdownError):
    pass


class SetProhibitedError(LockdownError):
    pass


class PairingDialogResponsePendingError(PairingError):
    pass


class UserDeniedPairingError(PairingError):
    pass


class InvalidHostIDError(PairingError):
    pass


class MissingValueError(LockdownError):
    pass


class InvalidConnectionError(LockdownError):
    pass


class PasscodeRequiredError(LockdownError):
    pass


class AmfiError(PlistException):
    pass


class DeviceHasPasscodeSetError(AmfiError):
    pass


class NotificationTimeoutError(PlistException, TimeoutError):
    pass


class ProfileError(PlistException):
    pass


class CloudConfigurationAlreadyPresentError(ProfileError):
    pass


class IRecvError(PlistException):
    pass


class IRecvNoDeviceConnectedError(IRecvError):
    pass


class MessageNotSupportedError(PlistException):
    pass


class InvalidServiceError(LockdownError):
    pass


class InspectorEvaluateError(PlistException):
    def __init__(self, class_name: str, message: str, line: Optional[int] = None, column: Optional[int] = None,
                 stack: Optional[list[str]] = None):
        super().__init__()
        self.class_name = class_name
        self.message = message
        self.line = line
        self.column = column
        self.stack = stack

    def __str__(self) -> str:
        stack_trace = '\n'.join([f'\t - {frame}' for frame in self.stack])
        return (f'{self.class_name}: {self.message}.\n'
                f'Line: {self.line} Column: {self.column}\n'
                f'Stack: {stack_trace}')


class LaunchingApplicationError(PlistException):
    pass


class AppInstallError(PlistException):
    pass


class AppNotInstalledError(PlistException):
    pass


class CoreDeviceError(PlistException):
    pass


class AccessDeniedError(PlistException):
    pass


class NoSuchBuildIdentityError(PlistException):
    pass


class MobileActivationException(PlistException):
    pass


class NotEnoughDiskSpaceError(PlistException):
    pass


class DeprecationError(PlistException):
    pass


class RSDRequiredError(PlistException):

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        super().__init__()


class SysdiagnoseTimeoutError(PlistException, TimeoutError):
    pass


class SupportError(PlistException):
    def __init__(self, os_name):
        self.os_name = os_name
        super().__init__()


class OSNotSupportedError(SupportError):
    pass


class FeatureNotSupportedError(SupportError):

    def __init__(self, os_name, feature):
        super().__init__(os_name)
        self.feature = feature


class QuicProtocolNotSupportedError(PlistException):
    pass


class RemotePairingCompletedError(PlistException):
    pass


class DisableMemoryLimitError(PlistException):
    pass


class ProtocolError(PlistException):
    pass
