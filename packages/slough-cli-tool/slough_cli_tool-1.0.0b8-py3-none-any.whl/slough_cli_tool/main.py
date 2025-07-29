"""Main module for slough-cli-tool."""

import sys

from slough.exceptions import SloughError
from slough_config.exceptions import SloughConfigError

from .cli_app import app
from .cli_error_handeling import display_error
from .exceptions import SloughCLIError


def main() -> None:  # pragma: no cover
    """Entry point for the slough-cli-tool."""
    try:
        app()
    except (SloughError, SloughCLIError, SloughConfigError) as exc:
        display_error(exc)
        sys.exit(1)
