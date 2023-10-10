import importlib
from pathlib import Path

import typer
from rich import print
from rich.tree import Tree

from agipack.builder import AGIPack, AGIPackConfig
from agipack.constants import AGIPACK_BASENAME, AGIPACK_SAMPLE_FILENAME

app = typer.Typer(invoke_without_command=True)


@app.callback()
def main(ctx: typer.Context):
    """Dockerfile generator for AGI -- nothing more, nothing less."""
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


@app.command()
def version():
    """Print the version number."""
    print(importlib.metadata.version("agi-pack"))


@app.command()
def init():
    """Generate a sample agibuild.yaml file."""
    config = AGIPackConfig.load_yaml(str(AGIPACK_SAMPLE_FILENAME))
    config.save_yaml(AGIPACK_BASENAME)
    print(f"🎉 Sample `{AGIPACK_BASENAME}` file generated.")
    print("-" * 40)
    with open(AGIPACK_BASENAME, "r") as f:
        print(f.read())
    print("-" * 40)
    print(f"👉 Edit {AGIPACK_BASENAME} and run `agi-pack generate -c {AGIPACK_BASENAME}` to generate the Dockerfile.")


DEFAULT_TARGET_NAME = Path.cwd().name.strip("/")


@app.command()
def generate(
    config_filename: str = typer.Option(
        AGIPACK_BASENAME, "--config", "-c", help="Path to the YAML configuration file."
    ),
    filename: str = typer.Option(
        "Dockerfile", "--output-filename", "-o", help="Output filename for the generated Dockerfile."
    ),
    python: str = typer.Option(
        None, "--python", "-p", help="Python version to use for the base image.", show_default=False
    ),
    base_image: str = typer.Option(
        None, "--base", "-b", help="Base image to use for the root/base target.", show_default=False
    ),
    prod: bool = typer.Option(False, "--prod", "-p", help="Generate a production Dockerfile.", show_default=False),
    lint: bool = typer.Option(False, "--lint", "-l", help="Lint the generated Dockerfile.", show_default=False),
    build: bool = typer.Option(False, "--build", "-b", help="Build the Docker image after generating the Dockerfile."),
):
    """Generate the Dockerfile with optional overrides.

    Usage:
        agi-pack generate -c agibuild.yaml
        agi-pack generate -c agibuild.yaml -o docker/Dockerfile
        agi-pack generate -c agibuild.yaml -p 3.8.10
        agi-pack generate -c agibuild.yaml -b python:3.8.10-slim
        agi-pack generate -c agibuild.yaml --prod --lint
    """
    # Load the YAML configuration
    config = AGIPackConfig.load_yaml(config_filename)

    # Override the python version and base image for the root image
    root = config.root()
    if python:
        config.images[root].python = python
    if base_image:
        config.images[root].base = base_image

    # Render the Dockerfiles with the new filename and configuration
    builder = AGIPack(config)
    dockerfiles = builder.render(filename=filename, env="prod" if prod else "dev")
    for target, filename in dockerfiles.items():
        image_config = config.images[target]

        cmd = f"docker build -f {filename} --target {target} -t {image_config.name}:{target} ."
        tree = Tree(f"📦 [bold white]{target}[/bold white]")
        tree.add(
            f"🎉 Successfully generated Dockerfile (target=[bold white]{target}[/bold white], filename=[bold white]{filename}[/bold white])."
        ).add(f"[green]`{cmd}`[/green]")
        print(tree)

        # Lint the generated Dockerfile using hadolint
        if lint:
            print(f"🔍 Linting Dockerfile for target [{target}]")
            builder.lint(filename=filename)

        # Build the Docker image using subprocess and print all the output as it happens
        if build:
            print(f"🚀 Building Docker image for target [{target}]")
            builder.build(filename=filename, target=target)


@app.command()
def build(
    config_filename: str = typer.Option(
        AGIPACK_BASENAME, "--config", "-c", help="Path to the YAML configuration file."
    ),
    filename: str = typer.Option(
        "Dockerfile", "--output-filename", "-o", help="Output filename for the generated Dockerfile."
    ),
    python: str = typer.Option(
        None, "--python", "-p", help="Python version to use for the base image.", show_default=False
    ),
    base_image: str = typer.Option(
        None, "--base", "-b", help="Base image to use for the root/base target.", show_default=False
    ),
    prod: bool = typer.Option(False, "--prod", "-p", help="Generate a production Dockerfile.", show_default=False),
    lint: bool = typer.Option(False, "--lint", "-l", help="Lint the generated Dockerfile.", show_default=False),
):
    """Generate the Dockerfile with optional overrides.

    Usage:
        agi-pack build -c agibuild.yaml
        agi-pack build -c agibuild.yaml -o docker/Dockerfile
        agi-pack build -c agibuild.yaml -p 3.8.10
        agi-pack build -c agibuild.yaml -b python:3.8.10-slim
        agi-pack build -c agibuild.yaml --prod --lint
    """
    generate(config_filename, filename, python, base_image, prod, lint, build=True)


if __name__ == "__main__":
    app()
