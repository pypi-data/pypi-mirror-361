"""CLI context for Slough CLI."""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path

from rich.logging import RichHandler

from slough.config_file_finder import ConfigFileFinder
from slough.slough import Slough
from slough.yaml_storage_manager import YAMLStorageManager

from .cli_output_visitor import (
    CLIOutputVisitor,
    ConsoleOutput,
    EnvironmentVariableOutput,
)


class CLIContext(ABC):
    """CLI context for CLI commands.

    Contains Factory methods for creating the logger, Slough object, and output
    visitor. This is used to create a context aware object that can be used by
    all commands. This is a common interface for all CLI commands.
    """

    @property
    @abstractmethod
    def logger(self) -> logging.Logger:
        """Retrieve a application wide logger.

        Returns:
            Logger: The application wide logger.
        """

    @property
    @abstractmethod
    def slough(self) -> Slough:
        """Retrieve the Slough object for the application.

        Returns:
            Slough: The application wide Slough object.
        """

    @property
    @abstractmethod
    def output_visitor(self) -> CLIOutputVisitor:
        """Retrieve the output visitor.

        Returns:
            CLIOutputVisitor: The application wide output visitor.
        """


class OutputType(str, Enum):
    """Output types for the CLI."""

    CONSOLE = 'console'
    ENV = 'env'
    EXPOTRED_ENV = 'exported-env'


class SloughCLIContext(CLIContext):
    """Concrete CLI Context for Slough CLI."""

    def __init__(
        self,
        logging_verbosity: int = 30,
        output_type: OutputType = OutputType.CONSOLE,
    ) -> None:
        """Initialize the Slough CLI context."""
        # Member variables
        self._logging_verbosity: int = logging_verbosity
        self._output_type: OutputType = output_type

        # Initialize the logger
        self._initialize_logger()

        # Objects
        self._cfg_file_path: Path = self._create_cfgfile_path()
        self._logger: logging.Logger | None = None
        self._slough: Slough | None = None
        self._cli_output_visitor: CLIOutputVisitor | None = None

    def _create_cfgfile_path(self) -> Path:
        """Create the configuration file path.

        Returns:
            Path: The configuration file path.
        """
        cfgfile_path = ConfigFileFinder(filename='slough.yml').find()
        if not cfgfile_path:
            cfgfile_path = Path.cwd() / 'slough.yml'
        return cfgfile_path

    @property
    def _logging_handlers(self) -> list[logging.Handler]:
        """Get the logging handlers.

        Returns:
            list[logging.Handler]: The logging handlers.
        """
        return [RichHandler()]

    def _initialize_logger(self) -> None:
        """Initialize the logger."""
        # Set up logging
        logging.basicConfig(
            level=self._logging_verbosity,
            format='"%(name)s": %(message)s',
            datefmt='[%X]',
            handlers=self._logging_handlers,
        )

    @property
    def logger(self) -> logging.Logger:
        """Retrieve a application wide logger.

        Returns:
            Logger: The application wide logger.
        """
        if not self._logger:
            self._logger = logging.getLogger('cli')
        return self._logger

    @property
    def slough(self) -> Slough:
        """Retrieve the Slough object for the application.

        Returns:
            Slough: The application wide Slough object.
        """
        # Create a Slough object
        if not self._slough:
            self._slough = Slough(
                storage_manager=YAMLStorageManager(self._create_cfgfile_path())
            )
        return self._slough

    def _create_output_visitor(self) -> CLIOutputVisitor:
        """Create the output visitor.

        Returns:
            CLIOutputVisitor: The application wide output visitor.
        """
        if self._output_type == OutputType.CONSOLE:
            return ConsoleOutput()
        elif self._output_type == OutputType.ENV:
            return EnvironmentVariableOutput()
        else:
            return EnvironmentVariableOutput(export=True)

    @property
    def output_visitor(self) -> CLIOutputVisitor:
        """Retrieve the output visitor.

        For now, this is a console output visitor. This will be used to
        output messages to the console.

        Returns:
            CLIOutputVisitor: The application wide output visitor.
        """
        if not self._cli_output_visitor:
            self._cli_output_visitor = self._create_output_visitor()
        return self._cli_output_visitor
