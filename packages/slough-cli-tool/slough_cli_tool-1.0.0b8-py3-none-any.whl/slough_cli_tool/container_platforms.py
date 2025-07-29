"""Container platforms part of the CLI tool."""

from enum import Enum

import typer

from slough.slough import Slough
from slough_cli_tool.cli_output_models import DataSetOutput
from slough_cli_tool.cli_output_visitor import CLIOutputVisitor

platforms = typer.Typer(no_args_is_help=True)


class ContainerPlatforms(str, Enum):
    """Container platforms for the CLI tool."""

    LINUX_AMD64 = 'linux/amd64'
    LINUX_ARM64 = 'linux/arm64'
    LINUX_ARM_V7 = 'linux/arm/v7'
    LINUX_ARM_V6 = 'linux/arm/v6'
    LINUX_PPC64LE = 'linux/ppc64le'
    LINUX_S390X = 'linux/s390x'
    LINUX_386 = 'linux/386'


@platforms.command(
    name='add',
    help='Add a container platform to a specific profile.',
    short_help='Add container platforms.',
)
def add_container_platforms(
    ctx: typer.Context,
    platforms: list[ContainerPlatforms] = typer.Argument(
        help='The platforms to add to the profile.'
    ),
    profile: str = typer.Option(
        default='_default',
        help='The profile to add the container platform to.',
    ),
) -> None:
    """Adds platforms to a profile.

    Args:
        ctx (typer.Context): Typer context
        platforms (list[str]): The platforms to add to the profile.
        profile (str, optional): The profile to add container platforms for.
            Defaults to the default profile.
    """
    slough: Slough = ctx.obj.slough
    with slough:
        slough.get_profile(
            profile
        ).get_container_configuration().add_platforms(
            [platform.value for platform in platforms]
        )


@platforms.command(
    name='list',
    help='List all available container platforms with their profile. You can '
    + 'enter a profile to see all platforms for that profile, including the '
    + '`_all` profile.',
    short_help='List all available container platforms.',
)
def list_container_platforms(
    ctx: typer.Context,
    profile: str = typer.Option(
        default='_default',
        help='The profile to list container platforms for.',
    ),
) -> None:
    """List all available container platforms with their profile.

    Args:
        ctx (typer.Context): Typer context
        profile (str, optional): The profile to list container platforms for.
            Defaults to None.
    """
    slough: Slough = ctx.obj.slough
    cfg_profile = slough.get_profile_with_all(profile)
    platforms = sorted(cfg_profile.get_container_configuration().platforms)

    os: CLIOutputVisitor = ctx.obj.output_visitor
    output_data = DataSetOutput(
        [
            'Platform',
        ]
    )
    output_data.data = [[platform] for platform in platforms]
    output_data.out(os)


@platforms.command(
    name='remove',
    help='Remove a container platform from a specific profile.',
    short_help='Remove container platforms.',
)
def remove_container_platforms(
    ctx: typer.Context,
    platforms: list[str] = typer.Argument(
        help='The platforms to remove from the profile.'
    ),
    profile: str = typer.Option(
        default='_default',
        help='The profile to remove the container platforms from.',
    ),
) -> None:
    """Removes platforms from a profile.

    Args:
        ctx (typer.Context): Typer context
        platforms (list[str]): The platforms to remove from the profile.
        profile (str, optional): The profile to remove the container platforms
            from. Defaults to the default profile.
    """
    slough: Slough = ctx.obj.slough
    with slough:
        slough.get_profile(
            profile
        ).get_container_configuration().remove_platforms(platforms)
