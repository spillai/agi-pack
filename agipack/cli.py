from pathlib import Path

import typer

from agipack.builder import AGIPack, AGIPackConfig
from agipack.constants import AGI_BUILD_FILENAME, AGI_BUILD_SAMPLE_FILENAME

DEFAULT_TARGET_NAME = Path.cwd().name.strip("/")

app = typer.Typer(invoke_without_command=True)


@app.callback()
def main(ctx: typer.Context):
    """Dockerfile generator for AGI -- nothing more, nothing less."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


@app.command()
def init():
    """Generate a sample agipack.yaml file."""
    config = AGIPackConfig.load_yaml(str(AGI_BUILD_SAMPLE_FILENAME))
    config.save_yaml(AGI_BUILD_FILENAME)
    typer.echo(f"🎉 Sample `{AGI_BUILD_FILENAME}` file generated.")
    typer.echo("-" * 40)
    with open(AGI_BUILD_FILENAME, "r") as f:
        typer.echo(f.read())
    typer.echo("-" * 40)
    typer.echo(
        f"👉 Edit {AGI_BUILD_FILENAME} and run `agi-pack generate -c {AGI_BUILD_FILENAME}` to generate the Dockerfile."
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
    """Generate the Dockerfile with optional overrides.

    Usage:
        agi-pack generate -c agipack.yaml
    """

    builder = AGIPack(config)
    builder.build_all()
    typer.echo(f"🎉 Dockerfile generated for `{target}`.")


if __name__ == "__main__":
    app()
