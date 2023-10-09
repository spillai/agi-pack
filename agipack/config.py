import logging
from dataclasses import asdict, field
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml
from pydantic import field_validator
from pydantic.dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Node:
    """Node in the dependency graph."""

    name: str
    """Name of the node."""

    root: bool = field(default=False)
    """Whether the node is the root node."""

    children: List[str] = field(default_factory=list)
    """List of children for the node."""

    def is_leaf(self) -> bool:
        """Check if the node is a leaf node."""
        return not len(self.children)


@dataclass
class ImageConfig:
    """AGIPack configuration for a docker target specified in `agibuild.yaml`

    images:
        <target>:
            image: <repository name>
            base: <base>
            env:
                <key>: <value>
            system:
                - <package>
            python: <version>
            pip:
                - <package>
            add:
                - <file>

    """

    image: str = field(default="agi:latest")
    """Name of the image repository.
    Defaults to the <target> name if not provided.
    """

    name: str = field(default="agi")
    """Pretty-name of the project and environment in the image."""

    base: str = field(default="debian:buster-slim")
    """Base docker image / target to use (FROM clause in the Dockerfile)."""

    env: Dict[str, str] = field(default_factory=dict)
    """List of environment variables to set."""

    system: Optional[List[str]] = field(default_factory=list)
    """List of system packages to install (via`apt-get`) ."""

    python: Optional[str] = field(default="3.8.10")
    """Python version to use (via `miniconda`)."""

    pip: Optional[List[str]] = field(default_factory=list)
    """List of Python packages to install (via `pip install`)."""

    requirements: Optional[List[str]] = field(default_factory=list)
    """List of Python requirements files to install (via `pip install -r`)."""

    add: Optional[List[str]] = field(default_factory=list)
    """List of files to copy into the image."""

    workdir: Optional[str] = field(default=None)
    """Working directory for the image (defaults to /app/${AGIPACK_ENV} if not set)."""

    run: Optional[List[str]] = field(default_factory=list)
    """List of commands to run in the image under the workdir."""

    entrypoint: Optional[List[str]] = field(default_factory=list)
    """Entrypoint for the image."""

    command: Optional[Union[str, List[str]]] = field(default_factory=lambda: ["bash"])
    """Command to run in the image."""

    def additional_kwargs(self):
        """Additional kwargs to pass to the Jinja2 Dockerfile template."""
        python_alias = f"py{''.join(self.python.split('.')[:2])}"
        return {"python_alias": python_alias}

    def dict(self):
        """Dictionary representation of the ImageConfig."""
        return {**asdict(self), **self.additional_kwargs()}

    def __repr__(self):
        """String representation of the ImageConfig."""
        return yaml.dump(self.dict(), sort_keys=False)

    def is_base_image(self) -> bool:
        """Check if the base target is root / does not have a parent."""
        return ":" in self.base

    @field_validator("python", mode="before")
    def validate_python_version(cls, python):
        """Validate the python version."""
        python = str(python)
        if not python.startswith("3."):
            raise ValueError(f"Python version must be >= 3.6 (found {python})")
        return python

    @field_validator("command", mode="before")
    def validate_command_version(cls, cmd):
        """Validate the command."""
        if isinstance(cmd, str):
            cmd = cmd.split(" ")
        elif isinstance(cmd, list):
            pass
        return cmd


@dataclass
class AGIPackConfig:
    """AGIPack configuration specified in `agibuild.yaml`

    images:
        base-cpu:
            image: autonomi/agi:latest-base-cpu
            base: python:3.8.10-slim
            env:
                MY_ENV: value

        base-dev:
            ...

        base-prod:
            ...
    """

    images: Dict[str, ImageConfig]
    """Dictionary of targets to build and their configurations."""

    def __post_init__(self):
        """Post-initialization hook."""
        self._target_tree: Dict[str, Node] = {}
        self._build_target_tree()

    def root(self) -> str:
        """Return the root target."""
        targets = [target for target, node in self._target_tree.items() if node.root]
        assert len(targets) == 1
        return targets[0]

    def children(self, target: str) -> List[str]:
        """Return the list of children for the given target."""
        return self._target_tree[target].children

    def is_root(self, target: str) -> bool:
        """Check if the given target is a base image."""
        return self._target_tree[target].root

    def is_prod(self) -> bool:
        """Check if the configuration is for production."""
        return self.prod

    @field_validator("images")
    def validate_python_dependencies_for_nonbase_images(cls, images):
        """Validate that all images have the same python dependency as the base image."""
        version = None
        for target, config in images.items():
            if config.is_base_image():
                version = config.python
            elif config.python != version:
                raise ValueError(f"Non-base image [{target}] must have the same python version as the base image")
        return images

    @classmethod
    def load_yaml(cls, filename: Union[str, Path]) -> "AGIPackConfig":
        """Load the AGIPack configuration from a YAML file.

        Args:
            filename (str): Path to the YAML file.
        Returns:
            AGIPackConfig: AGIPack configuration.
        """
        # Load the YAML file
        logger.debug(f"Loading AGIPack configuration from {filename}")
        with open(filename, "r") as f:
            data = yaml.safe_load(f)
        logger.debug(f"AGIPack configuration: {data}")

        # Validate the YAML file
        images = data.get("images", {})
        if not images:
            raise ValueError("No images specified in the YAML file")

        # Load default image target if not specified
        for target, config in data["images"].items():
            logger.debug(f"Processing target [{target}]")
            if "image" not in config:
                config["image"] = target
            data["images"][target] = ImageConfig(**config)
        logger.debug(f"AGIPack configuration: {data}")
        return cls(**data)

    def save_yaml(self, filename: str) -> None:
        """Save the AGIPack configuration to a YAML file.

        Args:
            filename (str): Path to the YAML file.
        """
        # Pre-process the config to remove empty lists, etc.
        data = asdict(self)
        for _, config in data["images"].items():
            for key in ["env", "system", "pip", "requirements", "add", "run", "entrypoint", "command"]:
                if not len(config[key]):
                    del config[key]
            for key in ["workdir"]:
                if config.get(key) is None:
                    del config[key]
        # Save the YAML file
        with open(filename, "w") as f:
            yaml.safe_dump(data, f, sort_keys=False)

    def _build_target_tree(self) -> None:
        """Build the target dependency tree."""
        for idx, (target, config) in enumerate(self.images.items()):
            logger.debug(f"{target} -> {config.base}")

            # Check if the first image is the base
            if idx == 0:
                if not config.is_base_image():
                    raise ValueError(f"First image [{target}] must be the base image")
                self._target_tree[target] = Node(name=target, root=True)
            else:
                assert config.base in self._target_tree
                self._target_tree[target] = Node(name=target)
                self._target_tree[config.base].children.append(target)
        logger.debug(f"Target dependencies: {self._target_tree}")
