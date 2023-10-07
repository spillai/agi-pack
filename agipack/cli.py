from pathlib import Path

import typer

from agipack.builder import AGIPack, AGIPackConfig
from agipack.constants import AGIPACK_BASENAME, AGIPACK_SAMPLE_FILENAME

app = typer.Typer(invoke_without_command=True)


@app.callback()
def main(ctx: typer.Context):
    """Dockerfile generator for AGI -- nothing more, nothing less."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


@app.command()
def init():
    """Generate a sample agipack.yaml file."""
    config = AGIPackConfig.load_yaml(str(AGIPACK_SAMPLE_FILENAME))
    config.save_yaml(AGIPACK_BASENAME)
    typer.echo(f"🎉 Sample `{AGIPACK_BASENAME}` file generated.")
    typer.echo("-" * 40)
    with open(AGIPACK_BASENAME, "r") as f:
        typer.echo(f.read())
    typer.echo("-" * 40)
    typer.echo(
        f"👉 Edit {AGIPACK_BASENAME} and run `agi-pack generate -c {AGIPACK_BASENAME}` to generate the Dockerfile."
    )


DEFAULT_TARGET_NAME = Path.cwd().name.strip("/")


@app.command()
def generate(
    config: str = typer.Option(AGIPACK_BASENAME, "--config", "-c", help="Path to the YAML configuration file."),
    target: str = typer.Option(DEFAULT_TARGET_NAME, "--target", "-t", help="Target image name."),
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
