#!/usr/bin/env python

# Copyright 2025 Pasteur Labs. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import re
import sys
import time
import webbrowser
from contextlib import nullcontext
from enum import Enum
from logging import getLogger
from pathlib import Path
from types import SimpleNamespace
from typing import Annotated, Any, NoReturn

import click
import typer
import yaml
from jinja2 import Environment, PackageLoader, StrictUndefined
from pydantic import ValidationError as PydanticValidationError
from rich.console import Console as RichConsole
from rich.table import Table as RichTable

from . import engine
from .api_parse import (
    EXPECTED_OBJECTS,
    TesseractBuildConfig,
    TesseractConfig,
    ValidationError,
    get_non_base_fields_in_tesseract_config,
)
from .config import get_config
from .docker_client import (
    APIError,
    BuildError,
    CLIDockerClient,
    Container,
    ContainerError,
    Image,
    ImageNotFound,
    NotFound,
)
from .exceptions import UserError
from .logs import DEFAULT_CONSOLE, set_logger

logger = getLogger("tesseract")

# Jinja2 Template Environment
ENV = Environment(
    loader=PackageLoader("tesseract_core.sdk", "templates"),
    undefined=StrictUndefined,
)

docker_client = CLIDockerClient()


class SpellcheckedTyperGroup(typer.core.TyperGroup):
    """A Typer group that suggests similar commands if a command is not found."""

    def get_command(self, ctx: click.Context, invoked_command: str) -> Any:
        """Get a command from the Typer group, suggesting similar commands if the command is not found."""
        import difflib

        possible_commands = self.list_commands(ctx)
        if invoked_command not in possible_commands:
            close_match = difflib.get_close_matches(
                invoked_command, possible_commands, n=1, cutoff=0.6
            )
            if close_match:
                raise click.UsageError(
                    f"No such command '{invoked_command}'. Did you mean '{close_match[0]}'?",
                    ctx,
                )
        return super().get_command(ctx, invoked_command)


app = typer.Typer(
    # Make -h an alias for --help
    context_settings={"help_option_names": ["-h", "--help"]},
    name="Tesseract",
    pretty_exceptions_show_locals=False,
    cls=SpellcheckedTyperGroup,
)

# Module-wide config
state = SimpleNamespace()
state.print_user_error_tracebacks = False

# Create a list of possible commands based on the ones in api_parse (kebab-cased)
POSSIBLE_CMDS = set(
    re.sub(r"([a-z])([A-Z])", r"\1-\2", object.name).replace("_", "-").lower()
    for object in EXPECTED_OBJECTS
)
POSSIBLE_CMDS.update({"health", "openapi-schema", "check", "check-gradients"})

# All fields in TesseractConfig and TesseractBuildConfig for config override
POSSIBLE_KEYPATHS = TesseractConfig.model_fields.keys()
# Check that the only field that has nested fields is build_config
assert len(get_non_base_fields_in_tesseract_config()) == 1
POSSIBLE_BUILD_CONFIGS = TesseractBuildConfig.model_fields.keys()

# Traverse templates folder to seach for recipes
AVAILABLE_RECIPES = set()
for temp_with_path in ENV.list_templates(extensions=["py"]):
    temp_with_path = Path(temp_with_path)
    if temp_with_path.name == "tesseract_api.py" and temp_with_path.parent:
        AVAILABLE_RECIPES.add(str(temp_with_path.parent))
AVAILABLE_RECIPES = sorted(AVAILABLE_RECIPES)


class LogLevel(str, Enum):
    """Available log levels for Tesseract CLI."""

    # Must be an enum to represent a choice in Typer
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


def _validate_tesseract_name(name: str | None) -> str:
    if name is None:
        if sys.stdout.isatty() and sys.stdin.isatty():
            name = typer.prompt("Enter a name for the Tesseract")
        else:
            raise typer.BadParameter(
                "Name must be provided as an argument or interactively."
            )

    forbidden_characters: str = ":;,.@#$%^&*()[]{}<>?|\\`~"
    if any(char in forbidden_characters for char in name) or any(
        char.isspace() for char in name
    ):
        raise typer.BadParameter(
            f"Name cannot contain whitespace or any of the following characters: {forbidden_characters}"
        )
    return name


def version_callback(value: bool | None) -> None:
    """Typer callback for version option."""
    if value:
        from tesseract_core import __version__

        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main_callback(
    loglevel: Annotated[
        LogLevel,
        typer.Option(
            help="Set the logging level. At debug level, also print tracebacks for user errors.",
            case_sensitive=False,
            show_default=True,
            metavar="LEVEL",
        ),
    ] = LogLevel.info,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Print Tesseract CLI version and exit.",
        ),
    ] = None,
) -> None:
    """Tesseract: A toolkit for re-usable, autodiff-native software components."""
    verbose_tracebacks = loglevel == LogLevel.debug
    state.print_user_error_tracebacks = verbose_tracebacks
    app.pretty_exceptions_show_locals = verbose_tracebacks

    set_logger(loglevel, catch_warnings=True, rich_format=True)

    try:
        get_config()
    except PydanticValidationError as err:
        message = [
            "Error while parsing Tesseract configuration. "
            "Please check your environment variables.",
            "Errors found:",
        ]
        for error in err.errors():
            message.append(
                f' - TESSERACT_{str(error["loc"][0]).upper()}="{error["input"]}": {error["msg"]}'
            )
        raise UserError("\n".join(message)) from None


def _parse_config_override(
    options: list[str] | None,
) -> dict[tuple[str, ...], Any]:
    """Parse `["path1.path2.path3=value"]` into `[(["path1", "path2", "path3"], "value")]`."""
    if options is None:
        return {}

    def _parse_option(option: str) -> tuple[tuple[str, ...], Any]:
        if "=" not in option:
            raise typer.BadParameter(
                f'Invalid config override "{option}" (must be `keypath=value`)',
                param_hint="config_override",
            )

        key, value = option.split("=", maxsplit=1)
        if not re.match(r"\w[\w|\.]*", key):
            raise typer.BadParameter(
                f'Invalid keypath "{key}" in config override "{option}"',
                param_hint="config_override",
            )

        path = tuple(key.split("."))

        try:
            value = yaml.safe_load(value)
        except yaml.YAMLError as e:
            raise typer.BadParameter(
                f'Invalid value for config override "{option}", could not parse value as YAML: {e}',
                param_hint="config_override",
            ) from e

        return path, value

    return dict(_parse_option(option) for option in options)


@app.command("build")
@engine.needs_docker
def build_image(
    src_dir: Annotated[
        Path,
        typer.Argument(
            help=(
                "Source directory for the Tesseract. Must contain `tesseract_api.py` "
                "and `tesseract_config.yaml`."
            ),
            dir_okay=True,
            exists=True,
            file_okay=False,
            readable=True,
        ),
    ],
    tag: Annotated[
        str | None,
        typer.Option(
            "--tag",
            "-t",
            help="Tag for the resulting Tesseract. This can help you distinguish between "
            "Tesseracts with the same base name, like `cfd:v1` and cfd:v2`, "
            "both named `cfd` but tagged as `v1` and `v2` respectively.",
        ),
    ] = None,
    build_dir: Annotated[
        Path | None,
        typer.Option(
            help="Directory to use for the build. Defaults to a temporary directory.",
            dir_okay=True,
            file_okay=False,
            writable=True,
        ),
    ] = None,
    forward_ssh_agent: Annotated[
        bool,
        typer.Option(
            help=(
                "Forward the SSH agent to the Docker build environment. "
                "Has to be provided if requirements.txt contains private dependencies."
            ),
        ),
    ] = False,
    config_override: Annotated[
        list[str] | None,
        typer.Option(
            help=(
                "Override a configuration option in the Tesseract. "
                "Format: ``keypath=value`` where ``keypath`` is a dot-separated path to the "
                "attribute in tesseract_config.yaml. "
                "Possible keypaths are: "
                f"{', '.join(POSSIBLE_KEYPATHS)}. \n"
                "\n Possible build_config options are: "
                f"{', '.join(POSSIBLE_BUILD_CONFIGS)}. \n"
                "\nExample: ``--config-override build_config.target_platform=linux/arm64``."
            ),
            metavar="KEYPATH=VALUE",
        ),
    ] = None,
    generate_only: Annotated[
        bool,
        typer.Option(
            help="Only generate the build context and do not actually build the image."
        ),
    ] = False,
) -> None:
    """Build a new Tesseract from a context directory.

    The passed directory must contain the files `tesseract_api.py` and `tesseract_config.yaml`
    (can be created via `tesseract init`).

    Prints the built images as JSON array to stdout, for example: `["mytesseract:latest"]`.
    If `--generate-only` is set, the path to the build context is printed instead.
    """
    if config_override is None:
        config_override = []

    parsed_config_override = _parse_config_override(config_override)

    if generate_only:
        progress_indicator = nullcontext()
    else:
        progress_indicator = DEFAULT_CONSOLE.status(
            "[white]Processing", spinner="dots", spinner_style="white"
        )

    try:
        with progress_indicator:
            build_out = engine.build_tesseract(
                src_dir,
                tag,
                build_dir=build_dir,
                inject_ssh=forward_ssh_agent,
                config_override=parsed_config_override,
                generate_only=generate_only,
            )
    except BuildError as e:
        # raise from None to Avoid overly long tracebacks,
        # all the information is in the printed logs / exception str already
        raise UserError(f"Error building Tesseract: {e}") from None
    except APIError as e:
        raise UserError(f"Docker server error: {e}") from e
    except TypeError as e:
        raise UserError(f"Input error building Tesseract: {e}") from e
    except PermissionError as e:
        raise UserError(f"Permission denied: {e}") from e
    except ValidationError as e:
        raise UserError(f"Error validating tesseract_api.py: {e}") from e

    if generate_only:
        # output is the path to the build context
        build_dir = build_out
        typer.echo(build_dir)
    else:
        # output is the built image
        image = build_out
        logger.info(f"Built image {image.short_id}, {image.tags}")
        typer.echo(json.dumps(image.tags))


@app.command("init")
def init(
    name: Annotated[
        # Guaranteed to be a string by _validate_tesseract_name
        str | None,
        typer.Option(
            help="Tesseract name as specified in tesseract_config.yaml. Will be prompted if not provided.",
            callback=_validate_tesseract_name,
            show_default=False,
        ),
    ] = None,
    target_dir: Annotated[
        Path,
        typer.Option(
            help="Path to the directory where the Tesseract API module should be created.",
            dir_okay=True,
            file_okay=False,
            writable=True,
            show_default="current directory",
        ),
    ] = Path("."),
    recipe: Annotated[
        str,
        typer.Option(
            click_type=click.Choice(AVAILABLE_RECIPES),
            help="Use a pre-configured template to initialize Tesseract API and configuration.",
        ),
    ] = "base",
) -> None:
    """Initialize a new Tesseract API module."""
    logger.info(f"Initializing Tesseract {name} in directory: {target_dir}")
    engine.init_api(target_dir, name, recipe=recipe)


def _validate_port(port: str | None) -> str | None:
    """Validate port input."""
    if port is None:
        return None

    port = port.strip()
    if "-" in port:
        start, end = port.split("-")
    else:
        start = end = port

    try:
        start, end = int(start), int(end)
    except ValueError as ex:
        raise typer.BadParameter(
            (f"Port '{port}' must be single integer or a range (e.g. -p '8000-8080')."),
            param_hint="port",
        ) from ex

    if start > end:
        raise typer.BadParameter(
            (
                f"Start port '{start}' must be less than "
                f"or equal to end port '{end}' (e.g. -p '8000-8080')."
            ),
            param_hint="port",
        )

    if not (0 <= start <= 65535) or not (0 <= end <= 65535):
        raise typer.BadParameter(
            f"Ports '{port}' must be between 0 and 65535.",
            param_hint="port",
        )
    return port


@app.command("serve")
@engine.needs_docker
def serve(
    image_names: Annotated[
        list[str],
        typer.Argument(..., help="One or more Tesseract image names"),
    ],
    volume: Annotated[
        list[str] | None,
        typer.Option(
            "-v",
            "--volume",
            help="Bind mount a volume in all Tesseracts, in Docker format: source:target[:ro|rw]",
            metavar="source:target",
            show_default=False,
        ),
    ] = None,
    environment: Annotated[
        list[str] | None,
        typer.Option(
            "--env",
            "-e",
            help="Set environment variables in the Tesseract containers, in Docker format: key=value.",
        ),
    ] = None,
    port: Annotated[
        str | None,
        typer.Option(
            "--port",
            "-p",
            help="Optional port/port range to serve the Tesseract on (e.g. -p '8080-8082'). "
            "Port must be between 1025 and 65535.",
            callback=_validate_port,
        ),
    ] = None,
    host_ip: Annotated[
        str,
        typer.Option(
            "--host-ip",
            help=(
                "IP address of the host to bind the Tesseract to. "
                "Defaults to 127.0.0.1 (localhost). To bind to all interfaces, use '0.0.0.0'. "
                "WARNING: This may expose Tesseract to all local networks, use with caution."
            ),
        ),
    ] = "127.0.0.1",
    gpus: Annotated[
        list[str] | None,
        typer.Option(
            "--gpus",
            metavar="'all' | int",
            help=(
                "IDs of host Nvidia GPUs to make available in the Tesseract. "
                "You can use all GPUs via `--gpus all` or pass (multiple) IDs: `--gpus 0 --gpus 1`."
            ),
        ),
    ] = None,
    num_workers: Annotated[
        int,
        typer.Option(
            "--num-workers",
            help="Number of worker processes to use when serving the Tesseract.",
            show_default=True,
        ),
    ] = 1,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            help=(
                "Enable debug mode. This will propagate full tracebacks to the client "
                "and start a debugpy server in the Tesseract. "
                "WARNING: This may expose sensitive information, use with caution (and never in production)."
            ),
        ),
    ] = False,
    no_compose: Annotated[
        bool,
        typer.Option(
            "--no-compose",
            help=(
                "Do not use Docker Compose to serve the Tesseract. "
                "Instead, the command will block until interrupted. "
                "This is useful for cases in which docker-compose is not available."
            ),
        ),
    ] = False,
    service_names: Annotated[
        str | None,
        typer.Option(
            "--service-names",
            help=(
                "Comma-separated list of service names by which each Tesseract should be exposed "
                "in the shared network. "
                "Tesseracts are reachable from one another at http://{service_name}:8000. "
                "Not supported when using --no-compose."
            ),
        ),
    ] = None,
    user: Annotated[
        str | None,
        typer.Option(
            "--user",
            help=(
                "User to run the Tesseracts as e.g. '1000' or '1000:1000' (uid:gid). "
                "Defaults to the current user."
            ),
        ),
    ] = None,
) -> None:
    """Serve one or more Tesseract images.

    A successful serve command will display on standard output a JSON object
    with the Docker Compose project ID, which is required to run the teardown
    command, as well as a list of all containers spawned and their respective
    ports.
    """
    if port is not None:
        if len(image_names) > 1:
            # TODO: Docker compose with multiple ports is not supported until
            # docker/compose#7188 is resolved.
            raise typer.BadParameter(
                (
                    "Port specification only works if exactly one Tesseract is being served. "
                    f"Currently attempting to serve `{len(image_names)}` Tesseracts."
                ),
                param_hint="image_names",
            )
        ports = [port]
    else:
        ports = None

    # Parse environment variables from list to dict
    if environment is not None:
        try:
            environment = {
                env.split("=", maxsplit=1)[0]: env.split("=", maxsplit=1)[1]
                for env in environment
            }
        except Exception as ex:
            raise typer.BadParameter(
                "Environment variables must be in the format 'key=value'.",
                param_hint="environment",
            ) from ex

    if service_names is not None:
        if no_compose:
            raise typer.BadParameter(
                "Service name specification only works with Docker Compose.",
                param_hint="service_names",
            )

        service_names_list = service_names.split(",")
    else:
        service_names_list = None

    try:
        project_id = engine.serve(
            image_names,
            host_ip,
            ports,
            volume,
            environment,
            gpus,
            debug,
            num_workers,
            no_compose,
            service_names_list,
            user,
        )
    except RuntimeError as ex:
        raise UserError(
            f"Internal Docker error occurred while serving Tesseracts: {ex}"
        ) from ex

    container_ports = _display_project_meta(project_id)
    logger.info(
        f"Tesseract project ID, use it with 'tesseract teardown' command: {project_id}"
    )
    project_meta = {"project_id": project_id, "containers": container_ports}
    json_info = json.dumps(project_meta)
    typer.echo(json_info, nl=False)


@app.command("list")
@engine.needs_docker
def list_tesseract_images() -> None:
    """Display all Tesseract images."""
    _display_tesseract_image_meta()


@app.command("ps")
@engine.needs_docker
def list_tesseract_containers() -> None:
    """Display all Tesseract containers."""
    _display_tesseract_containers_meta()


def _display_tesseract_image_meta() -> None:
    """Display Tesseract image metadata."""
    table = RichTable("ID", "Tags", "Name", "Version", "Description")
    images = docker_client.images.list()
    for image in images:
        tesseract_vals = _get_tesseract_env_vals(image)
        if tesseract_vals:
            table.add_row(
                # Checksum Type + First 12 Chars of ID
                image.id[:19],
                str(image.tags),
                tesseract_vals["TESSERACT_NAME"],
                tesseract_vals.get("TESSERACT_VERSION", ""),
                tesseract_vals.get("TESSERACT_DESCRIPTION", "").replace("\n", " "),
            )
    RichConsole().print(table)


def _display_tesseract_containers_meta() -> None:
    """Display Tesseract containers metadata."""
    table = RichTable(
        "ID", "Name", "Version", "Host Address", "Project ID", "Description"
    )
    containers = docker_client.containers.list()
    for container in containers:
        tesseract_vals = _get_tesseract_env_vals(container)
        if tesseract_vals:
            tesseract_project = _find_tesseract_project(container)
            table.add_row(
                container.id[:12],
                tesseract_vals["TESSERACT_NAME"],
                tesseract_vals["TESSERACT_VERSION"],
                f"{container.host_ip}:{container.host_port}",
                tesseract_project,
                tesseract_vals.get("TESSERACT_DESCRIPTION", "").replace("\\n", " "),
            )
    RichConsole().print(table)


def _get_tesseract_env_vals(
    docker_asset: Image | Container,
) -> dict:
    """Convert Tesseract environment variables from list to dictionary."""
    env_vals = [s for s in docker_asset.attrs["Config"]["Env"] if "TESSERACT_" in s]
    return {item.split("=")[0]: item.split("=")[1] for item in env_vals}


def _find_tesseract_project(
    tesseract: Container,
) -> str:
    """Find the Tesseract Project ID for a given tesseract.

    A Tesseract Project ID is either a Docker Compose ID or a container name.
    """
    if tesseract.project_id is not None:
        return tesseract.project_id

    tesseract_id = tesseract.id[:12]

    for project, containers in docker_client.compose.list().items():
        if tesseract_id in containers:
            return project

    return tesseract.name


@app.command("apidoc")
@engine.needs_docker
def apidoc(
    image_name: Annotated[
        str,
        typer.Argument(..., help="Tesseract image name"),
    ],
    browser: Annotated[
        bool,
        typer.Option(help="Open the browser after serving the OpenAPI schema"),
    ] = True,
) -> None:
    """Serve the OpenAPI schema for a Tesseract."""
    host_ip = "127.0.0.1"
    project_id = engine.serve([image_name], no_compose=True, host_ip=host_ip)
    try:
        container = docker_client.containers.get(project_id)
        url = f"http://{host_ip}:{container.host_port}/docs"
        logger.info(f"Serving OpenAPI docs for Tesseract {image_name} at {url}")
        logger.info("  Press Ctrl+C to stop")
        if browser:
            webbrowser.open(url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            return
    finally:
        engine.teardown(project_id)


def _display_project_meta(project_id: str) -> list:
    """Display project metadata.

    Returns a list of dictionaries {name: container_name, port: host_port}.
    """
    container_ports = []

    compose_projects = docker_client.compose.list()
    if project_id in compose_projects:
        containers = compose_projects[project_id]
    else:
        containers = [project_id]

    for container_id in containers:
        container = docker_client.containers.get(container_id)
        logger.info(f"Container ID: {container.id}")
        logger.info(f"Name: {container.name}")
        entrypoint = container.attrs["Config"]["Entrypoint"]
        logger.info(f"Entrypoint: {entrypoint}")
        host_port = container.host_port
        host_ip = container.host_ip
        logger.info(f"View Tesseract: http://{host_ip}:{host_port}/docs")
        container_ports.append(
            {"name": container.name, "port": host_port, "ip": host_ip}
        )
        if container.host_debugpy_port:
            logger.info(
                f"Debugpy server listening at http://{host_ip}:{container.host_debugpy_port}"
            )

    return container_ports


@app.command("teardown")
@engine.needs_docker
def teardown(
    project_ids: Annotated[
        list[str] | None,
        typer.Argument(..., help="Docker Compose project IDs"),
    ] = None,
    tear_all: Annotated[
        bool,
        typer.Option(
            "--all",
            help="Tear down all Tesseracts currently being served.",
        ),
    ] = False,
) -> None:
    """Tear down one or more Tesseracts that were previously started with `tesseract serve`.

    One or more Tesseract project ids must be specified unless `--all` is set.
    """
    if not project_ids and not tear_all:
        raise typer.BadParameter(
            "Either project IDs or --all flag must be provided",
            param_hint="project_ids",
        )

    if project_ids and tear_all:
        raise typer.BadParameter(
            "Either project IDs or --all flag must be provided, but not both",
            param_hint="project_ids",
        )

    try:
        if not project_ids:
            project_ids = []  # Pass in empty list if no project_ids are provided.
        engine.teardown(project_ids, tear_all=tear_all)
    except ValueError as ex:
        raise UserError(
            f"Input error occurred while tearing down Tesseracts: {ex}"
        ) from ex
    except RuntimeError as ex:
        raise UserError(
            f"Internal Docker error occurred while tearing down Tesseracts: {ex}"
        ) from ex
    except NotFound as ex:
        raise UserError(f"Tesseract Project ID not found: {ex}") from ex


def _sanitize_error_output(error_output: str, tesseract_image: str) -> str:
    """Remove references to tesseract-runtime and unavailable commands from error output."""
    # Replace references to tesseract-runtime with tesseract run
    error_output = re.sub(
        r"Try 'tesseract-runtime",
        f"Try 'tesseract run {tesseract_image}",
        error_output,
    )

    error_output = re.sub(
        r"Usage: tesseract-runtime",
        f"Usage: tesseract run {tesseract_image}",
        error_output,
    )

    # Hide commands in help strings that users are not supposed to use via tesseract run
    error_output = re.sub(
        r"^│\s+(serve|health)\s+.*?$\n",
        "",
        error_output,
        flags=re.MULTILINE,
    )

    return error_output


@app.command(
    "run",
    # We need to ignore unknown options to forward the args to the Tesseract container
    context_settings={"ignore_unknown_options": True},
    # We implement --help manually to forward the help of the Tesseract container
    add_help_option=False,
)
@engine.needs_docker
def run_container(
    context: click.Context,
    tesseract_image: Annotated[
        str,
        typer.Argument(help="Tesseract image name"),
    ],
    cmd: Annotated[
        str,
        typer.Argument(help="Tesseract command to run"),
    ] = "",
    args: Annotated[
        list[str] | None,
        typer.Argument(help="Arguments for the command"),
    ] = None,
    volume: Annotated[
        list[str] | None,
        typer.Option(
            "-v",
            "--volume",
            help="Bind mount a volume, in Docker format: source:target.",
            metavar="source:target",
            show_default=False,
        ),
    ] = None,
    gpus: Annotated[
        list[str] | None,
        typer.Option(
            "--gpus",
            metavar="'all' | int",
            help=(
                "IDs of host GPUs to make available in the tesseract. "
                "You can use all GPUs via `--gpus all` or pass (multiple) IDs: `--gpus 0 --gpus 1`."
            ),
        ),
    ] = None,
    environment: Annotated[
        list[str] | None,
        typer.Option(
            "--env",
            "-e",
            help="Set environment variables in the Tesseract container, in Docker format: key=value.",
            metavar="key=value",
            show_default=False,
        ),
    ] = None,
    user: Annotated[
        str | None,
        typer.Option(
            "--user",
            help=(
                "User to run the Tesseract as e.g. '1000' or '1000:1000' (uid:gid). "
                "Defaults to the current user."
            ),
        ),
    ] = None,
) -> None:
    """Execute a command in a Tesseract.

    This command starts a Tesseract instance and executes the given
    command.
    """
    if args is None:
        args = []

    if cmd == "serve":
        logger.error(
            "You should not serve tesseracts via "
            "`tesseract run <tesseract-name> serve`. "
            "Use `tesseract serve <tesseract-name>` instead."
        )
        raise typer.Exit(1)

    help_args = {"-h", "--help"}

    # When called as `tesseract run --help` -> show generic help
    if tesseract_image in help_args:
        context.get_help()
        return

    invoke_help = any(arg in help_args for arg in args) or cmd in help_args

    if (not cmd or cmd not in POSSIBLE_CMDS) and not invoke_help:
        if not cmd:
            error_string = f"Command is required. Are you sure your Tesseract image name is `{tesseract_image}`?\n"
        else:
            error_string = f"Command `{cmd}` does not exist. \n"

        error_string += (
            f"\nRun `tesseract run {tesseract_image} --help` for more information.\n"
        )

        error_string = (
            error_string + f"\nPossible commands are: {', '.join(POSSIBLE_CMDS)}"
        )
        raise typer.BadParameter(error_string, param_hint="cmd")

    if environment is not None:
        try:
            environment = {
                item.split("=", maxsplit=1)[0]: item.split("=", maxsplit=1)[1]
                for item in environment
            }
        except Exception as ex:
            raise typer.BadParameter(
                "Environment variables must be in the format 'key=value'.",
                param_hint="env",
            ) from ex
    try:
        result_out, result_err = engine.run_tesseract(
            tesseract_image,
            cmd,
            args,
            volumes=volume,
            gpus=gpus,
            environment=environment,
            user=user,
        )

    except ImageNotFound as e:
        raise UserError(
            "Tesseract image not found. "
            f"Are you sure your tesseract image name is {tesseract_image}?\n\n{e}"
        ) from e

    except ContainerError as e:
        msg = e.stderr.decode("utf-8").strip()
        if "No such command" in msg:
            error_string = f"Error running Tesseract '{tesseract_image}' \n\n Error: Unimplemented command '{cmd}'.  "
        else:
            error_string = _sanitize_error_output(
                f"Error running Tesseract. \n\n{msg}", tesseract_image
            )

        raise UserError(error_string) from e

    if invoke_help:
        result_err = _sanitize_error_output(result_err, tesseract_image)

    typer.echo(result_err, err=True, nl=False)
    typer.echo(result_out, nl=False)


def entrypoint() -> NoReturn:
    """Entrypoint for the Tesseract CLI."""
    try:
        result = app()
    except UserError as e:
        if state.print_user_error_tracebacks:
            # Do not print the exception here since it's part of the traceback
            logger.error("UserError occurred, traceback:", exc_info=True)
        else:
            # Prints only the error message without traceback
            logger.error(str(e), exc_info=False)
        result = 1
    except Exception:
        logger.critical("Uncaught error", exc_info=True)
        result = 2

    if result > 0:
        logger.critical("Aborting")

    raise SystemExit(result)


# Expose the underlying click object for doc generation
typer_click_object = typer.main.get_command(app)

if __name__ == "__main__":
    entrypoint()
