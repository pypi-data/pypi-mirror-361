"""Module that sets up the CLI Typer app."""

import logging

import typer

from slough import __version__ as slough_version
from slough_cli_tool.cli_context import (
    CLIContext,
    OutputType,
    SloughCLIContext,
)
from slough_cli_tool.cli_output_models import MessageOutput
from slough_cli_tool.cli_output_visitor import CLIOutputVisitor

from .config import config
from .container import container
from .dev_container import dev_container
from .profiles import profiles
from .project import project

app = typer.Typer(no_args_is_help=True)
app.add_typer(
    config,
    name='config',
    help='Commands to work with configuration.',
    short_help='Configuration related commands.',
)
app.add_typer(
    project,
    name='project',
    help='Manage the project.',
    short_help='Project related commands.',
)
app.add_typer(
    dev_container,
    name='dev-container',
    help='Generate and manage dev container configuration.',
    short_help='Dev container commands.',
)
app.add_typer(
    container,
    name='container',
    help='Manage container configuration.',
    short_help='Container commands.',
)
app.add_typer(
    profiles,
    name='profiles',
    help='Manage configuration profiles.',
    short_help='Configuration profiles.',
)


@app.callback()
def common_command_line_options(
    ctx: typer.Context,
    verbosity: int = typer.Option(
        0,
        '--verbosity',
        '-v',
        count=True,
        help='Increase output verbosity.',
        max=2,
    ),
    output: OutputType = typer.Option(
        OutputType.CONSOLE,
        help='Output format.',
        show_default=True,
    ),
) -> None:
    """Common options for all commands.

    This is run for all commands, and makes sure the correct configuration file
    is loaded.

    Args:
        ctx (typer.Context): Typer context object.
        cfgfile (str): Path to the configuration file.
        verbosity (int): Verbosity level.
        output (OutputType): Output format.
    """
    # Create a context for the CLI
    context: CLIContext = SloughCLIContext(
        logging_verbosity=logging.WARNING - verbosity * 10,
        output_type=output,
    )

    # Add the context to the Typer context
    ctx.obj = context

    # Logging output
    cli_logger = context.logger
    cli_logger.debug('Created context object')


@app.command(
    'version',
    help='Print the version of slough-cli-tool.',
    short_help='Print version.',
)
def version(ctx: typer.Context) -> None:
    """Print the version of slough-cli-tool.

    Args:
        ctx (typer.Context): Typer context object.
    """
    os: CLIOutputVisitor = ctx.obj.output_visitor
    output_data = MessageOutput(f'Slough CLI {slough_version}')
    output_data.out(os)
