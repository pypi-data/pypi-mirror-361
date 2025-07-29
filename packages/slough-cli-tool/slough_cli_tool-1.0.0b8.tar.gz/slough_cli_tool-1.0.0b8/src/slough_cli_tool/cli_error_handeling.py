"""Module with error handling for the CLI."""

import sys

from rich.console import Console


def display_error(exc: Exception) -> None:
    """Display an error message in the console.

    Args:
        exc (Exception): The exception instance.
    """
    class_list = get_exception_baseclasses(exc)
    console = Console(file=sys.stderr)
    for class_name in reversed(class_list):
        console.print(
            f'[red]{class_name}[/red] [green]>[/green] ',
            style='bold',
            end='',
        )
    console.print(str(exc), style='yellow')


def get_exception_baseclasses(
    exc: Exception,
) -> list[str]:
    """Get the base classes of an exception.

    Args:
        exc (Exception): The exception instance.

    Returns:
        list[str]: A list of base class names.
    """
    exception_class: type[Exception] = type(exc)
    class_list: list[str] = []
    while exception_class is not Exception:
        class_list.append(exception_class.__name__)
        exception_class = exception_class.__bases__[0]

    return class_list
