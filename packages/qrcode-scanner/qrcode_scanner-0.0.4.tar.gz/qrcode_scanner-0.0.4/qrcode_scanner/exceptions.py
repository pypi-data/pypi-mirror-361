class DeviceNotFoundError(Exception):
    """Exception raised when a device is not found."""


class DeviceConnectionError(Exception):
    """Exception raised when a device connection fails."""


class DeviceNotConnectedError(DeviceConnectionError):
    """Exception raised when a device is not connected."""


class DeviceReadError(Exception):
    """Exception raised when reading from a device fails."""


class DecodingError(Exception):
    """Exception raised when decoding data fails."""


class UnknownCharacterError(DeviceReadError):
    """Exception raised when an unknown character is encountered."""
