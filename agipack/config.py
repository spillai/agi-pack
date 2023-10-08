import logging
from dataclasses import asdict, field
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml
from pydantic import field_validator
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
        return {"python_alias": python_alias, "is_prod": False, "is_base_image": self.is_base_image()}

    def dict(self):
        """Dictionary representation of the ImageConfig."""
        return {**asdict(self), **self.additional_kwargs()}

    def __repr__(self):
        """String representation of the ImageConfig."""
        return yaml.dump(self.dict(), sort_keys=False)

    def is_base_image(self) -> bool:
        """Check if the base target is root / does not have a parent."""
        return ":" in self.base


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
            for key in ["env", "system", "pip", "requirements", "add", "run"]:
                if not len(config[key]):
                    del config[key]
        # Save the YAML file
        with open(filename, "w") as f:
            yaml.safe_dump(data, f, sort_keys=False)
