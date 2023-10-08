import logging
from dataclasses import asdict, field
from typing import Dict, List, Optional

import yaml
from pydantic.dataclasses import dataclass

logger = logging.getLogger(__name__)


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

    run: Optional[List[str]] = field(default_factory=list)
    """List of commands to run in the image."""

    def additional_kwargs(self):
        """Additional kwargs to pass to the Jinja2 Dockerfile template."""
        python_alias = f"py{''.join(self.python.split('.')[:2])}"
        return {"python_alias": python_alias, "prod": False}

    def dict(self):
        """Dictionary representation of the ImageConfig."""
        return {**asdict(self), **self.additional_kwargs()}

    def __repr__(self):
        """String representation of the ImageConfig."""
        return yaml.dump(self.dict(), sort_keys=False)


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

    _target_dependencies: Optional[Dict[str, List[str]]] = field(default=None, init=False)
    """Dictionary of targets and their parents."""

    def __post_init__(self):
        """Post-initialization hook."""
        self._build_target_dependencies()

    @classmethod
    def load_yaml(cls, filename: str) -> "AGIPackConfig":
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
            for key in ["env", "system", "pip", "requirements", "add", "run"]:
                if not len(config[key]):
                    del config[key]
        # Save the YAML file
        with open(filename, "w") as f:
            yaml.safe_dump(data, f, sort_keys=False)

    def _build_target_dependencies(self) -> None:
        """Build the tree of dependencies for all the targets."""
        self._target_dependencies = {}
        for target, config in self.images.items():
            print(f"🌳 {target} -> {config.base}")
            if config.base not in self._target_dependencies:
                self._target_dependencies[config.base] = []
                continue
            self._target_dependencies[config.base].append(target)
            print(f"🌳 {target} -> {config.base}")
