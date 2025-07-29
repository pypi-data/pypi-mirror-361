"""Dev Container part of the CLI tool."""

import typer

from dev_container_gen.dev_container_manager import DevContainerManager
from slough import Slough
from slough_config import DevelopmentEnvironment as DevEnv

dev_container = typer.Typer(no_args_is_help=True)

# Dictionary with all images for specific Dev Containers
DEV_CONTAINER_IMAGES = {
    DevEnv.CPP_GENERIC: 'dast1986/slough-dev-dc-cpp',
    DevEnv.NODEJS_GENERIC: 'dast1986/slough-dev-dc-nodejs',
    DevEnv.PYTHON_GENERIC: 'dast1986/slough-dev-dc-python',
    DevEnv.RUST_GENERIC: 'dast1986/slough-dev-dc-rust',
    DevEnv.GENERIC: 'dast1986/slough-dev-dc-generic-base',
    DevEnv.LISP_SCHEME_GENERIC: 'dast1986/slough-dev-dc-lisp-scheme',
    DevEnv.JAVA_GENERIC: 'dast1986/slough-dev-dc-java',
    DevEnv.ASM6502_GENERIC: 'dast1986/slough-dev-dc-asm-6502',
    DevEnv.ESP32_GENERIC: 'dast1986/slough-dev-dc-esp32',
}


@dev_container.command(
    name='generate-config',
    help='Initialize configuration for a dev container. This uses the '
    + '"dev-environment" value from the Slough configuration file to choose '
    + 'a specific container image.',
    short_help='Initialize a new project configuration.',
)
def cli_dev_container_generate_config(
    ctx: typer.Context,
    name: str | None = typer.Option(
        default=None,
        help='The name for the dev container',
    ),
    container_tag: str = typer.Option(
        default='latest',
        help='The tag for the dev container. Useful if you want a specific '
        + 'version.',
    ),
    bind_docker_socket: bool | None = typer.Option(
        default=None,
        help='Mount the Docker socket inside the dev container. This is '
        + 'useful if you want to build Docker images inside the dev '
        + 'container.',
    ),
) -> None:
    """Initialize configuration for a dev container.

    Args:
        ctx (typer.Context): The context object.
        name (str, optional): The name for the dev container. Defaults to None.
        container_tag (str, optional): The tag for the dev container. Defaults
            to 'latest'.
        bind_docker_socket (bool, optional): Mount the Docker socket inside the
            dev container. Defaults to False.
    """
    slough: Slough = ctx.obj.slough
    dev_environment = slough.config.development_environment or DevEnv.GENERIC
    image = DEV_CONTAINER_IMAGES.get(
        dev_environment, DEV_CONTAINER_IMAGES[DevEnv.GENERIC]
    )

    # Generate and save the configuration
    dc_gen = DevContainerManager(slough.config.project.name)
    dc_gen.update_configuration(
        name=name,
        bind_docker_socket=bind_docker_socket,
        image=image,
        tag=container_tag,
    )
    dc_gen.save()
