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
    """Generate a sample agipack.yaml file."""
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
    config: str = typer.Option(AGIPACK_BASENAME, "--config", "-c", help="Path to the YAML configuration file."),
    output_filename: str = typer.Option(
        "Dockerfile", "--output-filename", "-o", help="Output filename for the generated Dockerfile."
    ),
):
    """Generate the Dockerfile with optional overrides.

    Usage:
        agi-pack generate -c agipack.yaml
        agi-pack generate -c agipack.yaml -o docker/
    """
    builder = AGIPack(config, output_filename=output_filename)
    dockerfiles = builder.build_all()
    for target, filename in dockerfiles.items():
        tree = Tree(f"📦 [bold white]{target}[/bold white]")
        tree.add(
            f"🎉 Successfully generated Dockerfile (target=[bold white]{target}[/bold white], filename=[bold white]{filename}[/bold white])."
        ).add(f"[green]`docker build -f {filename} --target {target} .`[/green]")
        print(tree)


if __name__ == "__main__":
    app()
