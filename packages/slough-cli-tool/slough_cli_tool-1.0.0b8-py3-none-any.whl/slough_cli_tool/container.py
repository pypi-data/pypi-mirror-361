"""Container part of the CLI tool."""

from enum import Enum

import typer

from slough import Slough

from .container_platforms import platforms
from .container_tags import tags

container = typer.Typer(no_args_is_help=True)

container.add_typer(
    tags,
    name='tags',
    help='Manage container tags in specific profiles.',
    short_help='Manage container tags.',
)

container.add_typer(
    platforms,
    name='platforms',
    help='Manage container platforms in specific profiles.',
    short_help='Manage container platforms.',
)


class ContainerOptions(str, Enum):
    """Container options for the CLI tool."""

    REGISTRY = 'registry'
    IMAGE = 'image'


@container.command(
    name='set',
    help='Set a specific container configuration option',
    short_help='Update container configuration options.',
)
def set_configuration(
    ctx: typer.Context,
    setting: ContainerOptions = typer.Argument(help='The option to set'),
    value: str = typer.Argument(help='The value to set'),
    profile: str = typer.Option(
        '_default',
        '--profile',
        '-p',
        help='The profile to set the configuration for',
    ),
) -> None:
    """Sets a specific configuration option in the CLI tool.

    Args:
        ctx (typer.Context): Typer context
        setting (str): The option to set.
        value (str): The value to set.
        profile (str): The profile to set the configuration for.
    """
    slough: Slough = ctx.obj.slough
    with slough:
        setattr(
            slough.get_profile(profile).get_container_configuration(),
            setting.value,
            value,
        )
    pass
