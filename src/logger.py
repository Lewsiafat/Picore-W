"""
Lightweight logging system for MicroPython.
Provides configurable log levels for debugging and production use.
"""


class LogLevel:
    """Log level constants."""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    NONE = 4  # Disable all logging


class Logger:
    """
    Simple logger with configurable level.

    Usage:
        from logger import Logger, LogLevel

        log = Logger("MyModule")
        log.info("Starting...")
        log.debug("Debug details")

        # Change global level
        Logger.set_level(LogLevel.DEBUG)
    """

    _level = LogLevel.INFO  # Default level
    _level_names = ['DEBUG', 'INFO', 'WARN', 'ERROR']

    def __init__(self, module_name):
        """
        Create a logger for a specific module.

        Args:
            module_name: Name to prefix log messages with.
        """
        self._module = module_name

    @classmethod
    def set_level(cls, level):
        """
        Set the global logging level.

        Args:
            level: LogLevel constant (DEBUG, INFO, WARNING, ERROR, NONE).
        """
        cls._level = level

    @classmethod
    def get_level(cls):
        """Get the current global logging level."""
        return cls._level

    def _log(self, level, msg):
        """Internal logging method."""
        if level >= Logger._level:
            prefix = Logger._level_names[level] if level < len(Logger._level_names) else '?'
            print(f"[{prefix}] {self._module}: {msg}")

    def debug(self, msg):
        """Log a debug message (verbose, for development)."""
        self._log(LogLevel.DEBUG, msg)

    def info(self, msg):
        """Log an info message (normal operation)."""
        self._log(LogLevel.INFO, msg)

    def warning(self, msg):
        """Log a warning message (potential issues)."""
        self._log(LogLevel.WARNING, msg)

    def error(self, msg):
        """Log an error message (failures)."""
        self._log(LogLevel.ERROR, msg)
