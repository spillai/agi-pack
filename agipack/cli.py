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
):
    """Generate the Dockerfile with optional overrides.

    Usage:
        agi-pack generate -c agibuild.yaml
        agi-pack generate -c agibuild.yaml -o docker/Dockerfile
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
        tree = Tree(f"📦 [bold white]{target}[/bold white]")
        tree.add(
            f"🎉 Successfully generated Dockerfile (target=[bold white]{target}[/bold white], filename=[bold white]{filename}[/bold white])."
        ).add(f"[green]`docker build -f {filename} --target {target} .`[/green]")
        print(tree)


if __name__ == "__main__":
    app()
