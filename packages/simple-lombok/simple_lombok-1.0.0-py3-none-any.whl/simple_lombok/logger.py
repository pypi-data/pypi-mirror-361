# Created by nikitanovikov at 7/12/25

"""
Logging functionality for SimpleLombok.
Provides a simple colored console logging utility.

This module contains a Logger class with static methods for different logging levels.
Each method prints messages to the console with color-coded formatting to distinguish
between different types of log messages (debug, info, error, etc.).

The Logger class is designed to be simple to use with no configuration required,
making it ideal for quick debugging and information display in applications.
"""

class Logger:
    """
    A utility class that provides colored console logging functionality.

    This class contains static methods for different logging levels, each printing
    messages with distinct colors to make them easily distinguishable in console output.
    No instance of this class needs to be created as all methods are static.

    The available logging levels are:
    - debug: For detailed debugging information (purple)
    - info: For general information messages (blue)
    - error: For error messages (red)
    - warn: For warning messages (yellow)
    - success: For success messages (green)

    Examples
    --------
    >>> from simple_lombok.logger import Logger
    >>> Logger.debug("Debug information")
    [DEBUG]: Debug information
    >>> Logger.info("General information")
    [INFO]: General information
    >>> Logger.error("Error occurred")
    [ERROR]: Error occurred
    >>> Logger.warn("Warning message")
    [WARN]: Warning message
    >>> Logger.success("Operation successful")
    [SUCCESS]: Operation successful
    """

    @staticmethod
    def debug(message: any):
        """
        Prints a debug message to the console with purple color formatting.

        This method is intended for detailed debugging information that is typically
        only useful during development or troubleshooting.

        Parameters
        ----------
        message : any
            The message to be logged. Can be any type that can be converted to a string.

        Examples
        --------
        >>> Logger.debug("Connection attempt failed, retrying...")
        [DEBUG]: Connection attempt failed, retrying...
        """
        print(f'\033[1;35m[DEBUG]:\033[0m {message}')

    @staticmethod
    def info(message: any):
        """
        Prints an informational message to the console with blue color formatting.

        This method is intended for general information messages that are useful
        during normal operation of an application.

        Parameters
        ----------
        message : any
            The message to be logged. Can be any type that can be converted to a string.

        Examples
        --------
        >>> Logger.info("Application started successfully")
        [INFO]: Application started successfully
        """
        print(f'\033[1;34m[INFO]:\033[0m {message}')

    @staticmethod
    def error(message: any):
        """
        Prints an error message to the console with red color formatting.

        This method is intended for error messages that indicate something has gone
        wrong in the application, such as exceptions or failed operations.

        Parameters
        ----------
        message : any
            The message to be logged. Can be any type that can be converted to a string.

        Examples
        --------
        >>> Logger.error("Failed to connect to database")
        [ERROR]: Failed to connect to database
        """
        print(f'\033[1;31m[ERROR]:\033[0m {message}')

    @staticmethod
    def warn(message: any):
        """
        Prints a warning message to the console with yellow color formatting.

        This method is intended for warning messages that indicate potential issues
        or situations that are not errors but might require attention.

        Parameters
        ----------
        message : any
            The message to be logged. Can be any type that can be converted to a string.

        Examples
        --------
        >>> Logger.warn("Disk space is running low")
        [WARN]: Disk space is running low
        """
        print(f'\033[1;33m[WARN]:\033[0m {message}')

    @staticmethod
    def success(message: any):
        """
        Prints a success message to the console with green color formatting.

        This method is intended for success messages that indicate operations or
        processes have completed successfully.

        Parameters
        ----------
        message : any
            The message to be logged. Can be any type that can be converted to a string.

        Examples
        --------
        >>> Logger.success("Data successfully saved to database")
        [SUCCESS]: Data successfully saved to database
        """
        print(f'\033[1;32m[SUCCESS]:\033[0m {message}')
