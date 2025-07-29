"""Module with output models."""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .cli_output_visitor import CLIOutputVisitor


class CLIOutputModel(ABC):
    """Base class for cli output models."""

    @abstractmethod
    def out(self, visitor: 'CLIOutputVisitor') -> None:
        """Output the model using the given visitor.

        Args:
            visitor (OutputVisitor): The output visitor to use.
        """


class DataSetOutput(CLIOutputModel):
    """Class for outputting a dataset."""

    def __init__(self, fields: list[str]) -> None:
        """Set the data to be output.

        Args:
            fields (list[str]): The fields of the dataset.
        """
        self._fields = fields
        self._data: list[Iterable[str]] = []

    @property
    def data(self) -> list:
        """Get the data to be output.

        Returns:
            list: The data to be output.
        """
        return self._data

    @data.setter
    def data(self, data: list[Iterable[str]]) -> None:
        """Set the data to be output.

        Args:
            data (list): The data to be output.
        """
        self._data = data

    @property
    def fields(self) -> list[str]:
        """Get the fields of the dataset.

        Returns:
            list[str]: The fields of the dataset.
        """
        return self._fields

    def out(self, visitor: 'CLIOutputVisitor') -> None:
        """Output the model using the given visitor.

        Args:
            visitor (OutputVisitor): The output visitor to use.
        """
        visitor.out_dataset(self)


class MessageOutput(CLIOutputModel):
    """Class for outputting a message."""

    def __init__(self, message: str) -> None:
        """Set the message to be output.

        Args:
            message (str): The message to be output.
        """
        self._message = message

    @property
    def message(self) -> str:
        """Get the message to be output.

        Returns:
            str: The message to be output.
        """
        return self._message

    def out(self, visitor: 'CLIOutputVisitor') -> None:
        """Output the model using the given visitor.

        Args:
            visitor (OutputVisitor): The output visitor to use.
        """
        visitor.out_message(self)
