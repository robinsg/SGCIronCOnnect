# framework/core/exceptions.py

class TerminalError(Exception):
    """Base exception for terminal-related errors."""
    pass

class TerminalTimeoutError(TerminalError):
    """Raised when a terminal operation times out."""
    pass

class ScreenMismatchError(TerminalError):
    """Raised when the current screen does not match the expected state."""
    pass

class ConnectionLostError(TerminalError):
    """Raised when the connection to the terminal is lost."""
    pass

class InputInhibitedError(TerminalError):
    """Raised when terminal is in an input-inhibited state and unable to accept input."""
    pass

class HandlerException(Exception):
    """Base exception for handler operations."""
    pass

class HandlerValidationError(HandlerException):
    """Raised when handler configuration is invalid."""
    pass

class HandlerExecutionError(HandlerException):
    """Raised when handler execution fails."""
    pass

class HandlerConfigMissingError(HandlerValidationError):
    """Raised when required handler config field is missing."""
    pass
