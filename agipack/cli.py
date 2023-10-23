from pathlib import Path

import typer
from rich import print
from rich.tree import Tree

from agipack.builder import AGIPack, AGIPackConfig
from agipack.constants import AGIPACK_BASENAME, AGIPACK_SAMPLE_FILENAME
from agipack.version import __version__

app = typer.Typer(invoke_without_command=True)


@app.callback()
def main(ctx: typer.Context):
    """Dockerfile generator for AGI -- nothing more, nothing less."""
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


@app.command()
def version():
    """Print the version number."""
    print(__version__)


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
    tag: str = typer.Option("{name}:{target}", "--tag", "-t", help="Image tag f-string.", show_default=True),
    target: str = typer.Option(None, "--target", help="Build specific target.", show_default=False),
    prod: bool = typer.Option(False, "--prod", help="Generate a production Dockerfile.", show_default=False),
    lint: bool = typer.Option(False, "--lint", help="Lint the generated Dockerfile.", show_default=False),
    build: bool = typer.Option(False, "--build", help="Build the Docker image after generating the Dockerfile."),
    skip_base_builds: bool = typer.Option(
        False, "--skip-base", help="Skip building the base image.", show_default=False
    ),
    push: bool = typer.Option(False, "--push", help="Push image to container repository.", show_default=False),
):
    r"""Generate the Dockerfile with optional overrides.

    Usage:\n
        agi-pack generate -c agibuild.yaml\n
        agi-pack generate -c agibuild.yaml -o docker/Dockerfile\n
        agi-pack generate -c agibuild.yaml -p 3.8.10\n
        agi-pack generate -c agibuild.yaml -b python:3.8.10-slim\n
        agi-pack generate -c agibuild.yaml -t "my-image-name:{target}"\n
        agi-pack generate -c agibuild.yaml --prod --lint\n
        agi-pack generate -c agibuild.yaml --build --push\n
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
    trees = []
    builder = AGIPack(config)
    dockerfiles = builder.render(filename=filename, env="prod" if prod else "dev", skip_base_builds=skip_base_builds)
    for docker_target, filename in dockerfiles.items():
        # Skip if the target is not the one we want to build
        if target is not None and docker_target != target:
            continue
        image_config = config.images[docker_target]

        # Build the Dockerfile using the generated filename and target
        tag_name = (
            f"{image_config.name}:{docker_target}"
            if tag is None
            else tag.format(name=image_config.name, target=docker_target)
        )
        cmd = f"docker build -f {filename} --target {docker_target} -t {tag_name} ."

        # Print the command to build the Dockerfile
        tree = Tree(f"📦 [bold white]{docker_target}[/bold white]")
        tree.add(
            f"[bold green]✓[/bold green] Successfully generated Dockerfile (target=[bold white]{docker_target}[/bold white], filename=[bold white]{filename}[/bold white])."
        ).add(f"[green]`{cmd}`[/green]")
        print(tree)

        # Lint the generated Dockerfile using hadolint
        if lint:
            print(f"🔍 Linting Dockerfile for target [{docker_target}]")
            builder.lint(filename=filename)

        # Build the Docker image using subprocess and print all the output as it happens
        if build:
            print(f"🚀 Building Docker image for target [{docker_target}]")
            builder.build(filename=filename, target=docker_target, tags=[tag_name], push=push)

            tree.add(
                f"[bold green]✓[/bold green] Successfully built image (target=[bold white]{docker_target}[/bold white], image=[bold white]{tag_name}[/bold white])."
            )
            # Push the Docker image to the container repository
            if push:
                tree.add(
                    f"[bold green]✓[/bold green] Successfully pushed image (target=[bold white]{docker_target}[/bold white], image=[bold white]{tag_name}[/bold white])."
                )
            trees.append(tree)

    # Re-render the tree
    for tree in trees:
        print(tree)


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
    tag: str = typer.Option("{name}:{target}", "--tag", "-t", help="Image tag f-string.", show_default=True),
    target: str = typer.Option(None, "--target", help="Build specific target.", show_default=False),
    prod: bool = typer.Option(False, "--prod", help="Generate a production Dockerfile.", show_default=False),
    lint: bool = typer.Option(False, "--lint", help="Lint the generated Dockerfile.", show_default=False),
    skip_base_builds: bool = typer.Option(
        False, "--skip-base", help="Skip building the base image.", show_default=False
    ),
    push: bool = typer.Option(False, "--push", help="Push image to container repository.", show_default=False),
):
    """Generate the Dockerfile with optional overrides.

    Usage:\n
        agi-pack build -c agibuild.yaml\n
        agi-pack build -c agibuild.yaml -o docker/Dockerfile\n
        agi-pack build -c agibuild.yaml -p 3.8.10\n
        agi-pack build -c agibuild.yaml -b python:3.8.10-slim\n
        agi-pack build -c agibuild.yaml -t "my-image-name:{target}"\n
        agi-pack build -c agibuild.yaml -t "my-image-name:my-target"\n
        agi-pack build -c agibuild.yaml --prod --lint\n
        agi-pack build -c agibuild.yaml --push\n
    """
    generate(
        config_filename,
        filename,
        python=python,
        base_image=base_image,
        tag=tag,
        target=target,
        prod=prod,
        lint=lint,
        build=True,
        skip_base_builds=skip_base_builds,
        push=push,
    )


if __name__ == "__main__":
    app()
