"""Visitors for outputting data."""

from abc import ABC, abstractmethod

from rich import box
from rich.console import Console
from rich.table import Table

from slough_cli_tool.exceptions import OutputTypeUnsupportedError

from .cli_output_models import DataSetOutput, MessageOutput


class CLIOutputVisitor(ABC):
    """Base class for output visitors."""

    @abstractmethod
    def out_dataset(self, model: DataSetOutput) -> None:
        """Output the dataset using the given visitor.

        Args:
            model (DataSetOutput): The dataset to output.
        """

    @abstractmethod
    def out_message(self, model: MessageOutput) -> None:
        """Output the message using the given visitor.

        Args:
            model (MessageOutput): The message to output.
        """


class ConsoleOutput(CLIOutputVisitor):
    """Output visitor that uses the console for output."""

    def __init__(self) -> None:
        """Initialize the console output visitor."""
        self._console = Console()

    def out_dataset(self, model: DataSetOutput) -> None:
        """Output the dataset using the console.

        Args:
            model (DataSetOutput): The dataset to output.
        """
        table = Table(box=box.SIMPLE)
        for column in model.fields:
            table.add_column(column)

        for row in model.data:
            table.add_row(*row)

        self._console.print(table)

    def out_message(self, model: MessageOutput) -> None:
        """Output the message using the console.

        Args:
            model (MessageOutput): The message to output.
        """
        self._console.print(model.message)


class EnvironmentVariableOutput(CLIOutputVisitor):
    """Output visitor that uses environment variables for output."""

    def __init__(self, export: bool = False) -> None:
        """Initialize the environment variable output visitor.

        Args:
            export (bool): Whether to export the variables or not.
        """
        self._export = export

    def out_dataset(self, model: DataSetOutput) -> None:
        """Output the variables using the environment variable output.

        This requires data in the following format: a list with a tuple with
        exactly two elements: the variable name and the value. If this isn't
        given, an error will be raised.

        Args:
            model (DataSetOutput): The dataset to output.
        """
        for item in model.data:
            if len(item) != 2:
                raise OutputTypeUnsupportedError(
                    'This output type is not valid for this type of data.'
                )
            if self._export:
                print('export ', end='')
            variable_name = item[0].upper().replace('.', '_')
            print(f'{variable_name}="{item[1]}"')

    def out_message(self, model: MessageOutput) -> None:
        """Output the message using the environment variable output.

        Args:
            model (MessageOutput): The message to output.
        """
        print(f'MESSAGE="{model.message}"')
