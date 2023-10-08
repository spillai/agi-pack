from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field


class ImageConfig(BaseModel):
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

    image: str = Field(default="agi:latest")
    """Name of the image repository.
    Defaults to the <target> name if not provided.
    """

    name: str = Field(default="agi")
    """Pretty-name of the project and environment in the image."""

    base: str = Field(default="debian:buster-slim")
    """Base docker image to use (FROM clause in the Dockerfile)."""

    env: Dict[str, str] = Field(default_factory=dict)
    """List of environment variables to set."""

    system: Optional[List[str]] = Field(default_factory=list)
    """List of system packages to install (via`apt-get`) ."""

    python: Optional[str] = Field(default="3.8.10")
    """Python version to use (via `miniconda`)."""

    pip: Optional[List[str]] = Field(default_factory=list)
    """List of Python packages to install (via `pip install`)."""

    requirements: Optional[List[str]] = Field(default_factory=list)
    """List of Python requirements files to install (via `pip install -r`)."""

    add: Optional[List[str]] = Field(default_factory=list)
    """List of files to copy into the image."""

    run: Optional[List[str]] = Field(default_factory=list)
    """List of commands to run in the image."""

    def additional_kwargs(self):
        """Additional kwargs to pass to the Jinja2 Dockerfile template."""
        python_alias = f"py{''.join(self.python.split('.')[:2])}"
        return {"python_alias": python_alias, "prod": False}

    def model_dump(self):
        return {**super().model_dump(), **self.additional_kwargs()}


class AGIPackConfig(BaseModel):
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

    @classmethod
    def load_yaml(cls, filename: str) -> "AGIPackConfig":
        """Load the AGIPack configuration from a YAML file.

        Args:
            filename (str): Path to the YAML file.
        Returns:
            AGIPackConfig: AGIPack configuration.
        """
        # Load the YAML file
        with open(filename, "r") as f:
            data = yaml.safe_load(f)

        # Load default image target if not specified
        for target, config in data["images"].items():
            if "image" not in config:
                config["image"] = target
            data["images"][target] = ImageConfig(**config)
        return cls(**data)

    def save_yaml(self, filename: str) -> None:
        """Save the AGIPack configuration to a YAML file.

        Args:
            filename (str): Path to the YAML file.
        """
        # Pre-process the config to remove empty lists, etc.
        data = self.model_dump()
        for _, config in data["images"].items():
            for key in ["env", "system", "pip", "requirements", "add", "run"]:
                if not len(config[key]):
                    del config[key]
        # Save the YAML file
        with open(filename, "w") as f:
            yaml.safe_dump(data, f, sort_keys=False)
