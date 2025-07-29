"""Container tags part of the CLI tool."""

import typer

from slough.slough import Slough
from slough_cli_tool.cli_output_models import DataSetOutput
from slough_cli_tool.cli_output_visitor import CLIOutputVisitor

tags = typer.Typer(no_args_is_help=True)


@tags.command(
    name='add',
    help='Add a container tag to a specific profile.',
    short_help='Add container tags.',
)
def add_container_tags(
    ctx: typer.Context,
    tags: list[str] = typer.Argument(help='The tags to add to the profile.'),
    profile: str = typer.Option(
        default='_default',
        help='The profile to add the container tag to.',
    ),
) -> None:
    """Adds tags to a profile.

    Args:
        ctx (typer.Context): Typer context
        tags (list[str]): The tags to add to the profile.
        profile (str, optional): The profile to add container tags for.
            Defaults to the default profile.
    """
    slough: Slough = ctx.obj.slough
    with slough:
        slough.get_profile(profile).get_container_configuration().add_tags(
            tags
        )


@tags.command(
    name='list',
    help='List all available container tags with their profile. You can '
    + 'enter a profile to see all tags for that profile, including the '
    + '`_all` profile.',
    short_help='List all available container tags.',
)
def list_container_tags(
    ctx: typer.Context,
    profile: str = typer.Option(
        default='_default',
        help='The profile to list container tags for.',
    ),
) -> None:
    """List all available container tags with their profile.

    Args:
        ctx (typer.Context): Typer context
        profile (str, optional): The profile to list container tags for.
            Defaults to None.
    """
    slough: Slough = ctx.obj.slough
    cfg_profile = slough.get_profile_with_all(profile)
    tags = sorted(cfg_profile.get_container_configuration().tags)

    os: CLIOutputVisitor = ctx.obj.output_visitor
    output_data = DataSetOutput(
        [
            'Tagname',
        ]
    )
    output_data.data = [[tag] for tag in tags]
    output_data.out(os)


@tags.command(
    name='remove',
    help='Remove a container tag from a specific profile.',
    short_help='Remove container tags.',
)
def remove_container_tags(
    ctx: typer.Context,
    tags: list[str] = typer.Argument(
        help='The tags to remove from the profile.'
    ),
    profile: str = typer.Option(
        default='_default',
        help='The profile to remove the container tags from.',
    ),
) -> None:
    """Removes tags from a profile.

    Args:
        ctx (typer.Context): Typer context
        tags (list[str]): The tags to remove from the profile.
        profile (str, optional): The profile to remove the container tags from.
            Defaults to the default profile.
    """
    slough: Slough = ctx.obj.slough
    with slough:
        slough.get_profile(profile).get_container_configuration().remove_tags(
            tags
        )
