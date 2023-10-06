from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field


class ImageConfig(BaseModel):
    """AGIPack configuration for a docker target specified in `agipack.yaml`

    images:
        <target>:
            name: <name>
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

    name: str = Field(default="agi")
    """Name of the image."""

    base: str = Field(default="python:3.8.10-slim")
    """Base docker image to use (FROM clause in the Dockerfile)."""

    env: Dict[str, str] = Field(default_factory=dict)
    """List of environment variables to set."""

    system: Optional[List[str]] = Field(default_factory=list)
    """List of system packages to install (via`apt-get`) ."""

    python: Optional[str] = Field(default="3.8.10")
    """Python version to use (via `miniconda`)."""

    pip: Optional[List[str]] = Field(default_factory=list)
    """List of Python packages to install (via `pip`)."""

    add: Optional[List[str]] = Field(default_factory=list)
    """List of files to copy into the image."""

    def additional_kwargs(self):
        """Additional kwargs to pass to the Jinja2 Dockerfile template."""
        python_alias = f"py{''.join(self.python.split('.')[:2])}"
        return {"python_alias": python_alias, "prod": False}

    def dict(self):
        return {**super().dict(), **self.additional_kwargs()}


class AGIPackConfig(BaseModel):
    """AGIPack configuration specified in `agipack.yaml`

    images:
        agi-base:
            name: agi-basename
            base: python:3.8.10-slim
            env:
                MY_ENV: value

        agi-base-dev:
            ...

        agi-base-prod:
            ...
    """

    images: Dict[str, ImageConfig]

    @classmethod
    def load_yaml(cls, filename: str) -> None:
        with open(filename, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def save_yaml(self, filename: str) -> None:
        with open(filename, "w") as f:
            yaml.safe_dump(self.dict(), f, sort_keys=False)
