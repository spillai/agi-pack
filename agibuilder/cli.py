from pathlib import Path

import typer

from agibuilder.builder import AGIBuilder
from agibuilder.constants import AGI_BUILD_FILENAME, AGI_BUILD_SAMPLE_FILENAME

DEFAULT_TARGET_NAME = Path.cwd().name.strip("/")

app = typer.Typer(invoke_without_command=True)


@app.callback()
def main(ctx: typer.Context):
    """
    🛠️  Dockerfile generator for AGI -- nothing more, nothing less.

    Usage:
        # Create a sample agibuild.yaml
        agibuilder init
        🎉 Sample agibuild.yaml file generated.

        # Generate a Dockerfile from an agibuild.yaml
        agibuilder generate -c agibuild.yaml
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


@app.command()
def init():
    """🚀 Generate a sample agibuild.yaml file.

    Example:
    agibuilder init
    """
    # Open the sample config yaml file
    builder = AGIBuilder(str(AGI_BUILD_SAMPLE_FILENAME))
    builder.save_yaml(AGI_BUILD_FILENAME)
    typer.echo(f"🎉 Sample {AGI_BUILD_FILENAME} file generated.")
    typer.echo(
        f"👉 Edit {AGI_BUILD_FILENAME} and run `agibuilder generate -c {AGI_BUILD_FILENAME}` to generate the Dockerfile."
    )


@app.command()
def generate(
    config: str = typer.Option(AGI_BUILD_FILENAME, help="Path to the YAML configuration file."),
    target: str = typer.Option(DEFAULT_TARGET_NAME, help="Target image name."),
    cuda: str = typer.Option(None, help="Override CUDA version."),
    python: str = typer.Option(None, help="Override Python version."),
    system: str = typer.Option(None, help="Override system packages."),
    packages: str = typer.Option(None, help="Override Python packages."),
    env: str = typer.Option(None, help="Override environment variables."),
):
    """🛠️ Generate the Dockerfile with optional overrides.

    Usage:
        agibuilder generate -c agibuild.yaml
    """
    overrides = {
        "target": target,
        "cuda": cuda,
        "python": python,
        "system": system,
        "packages": packages,
        "env": env,
    }
    builder = AGIBuilder(config, **overrides)

    # Apply overrides if provided
    # if cuda:
    #     builder.config.images[target].from_ = builder.config.images[target].from_.replace("cuda:", f"cuda:{cuda}")
    # if python:
    #     builder.config.images[target].python.version = python

    builder.generate_all()


if __name__ == "__main__":
    app()
