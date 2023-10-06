from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ImageConfig(BaseModel):
    name: str = Field(default="agi")
    base: str = Field(default="python:3.8.10-slim")
    env: Dict[str, str] = Field(default_factory=dict)
    system: Optional[List[str]] = Field(default_factory=list)
    python: Optional[str] = Field(default="3.8.10")
    pip: Optional[List[str]] = Field(default_factory=list)
    add: Optional[List[str]] = Field(default_factory=list)

    def additional_kwargs(self):
        python_alias = f"py{''.join(self.python.split('.')[:2])}"
        return {"python_alias": python_alias, "prod": False}

    def dict(self):
        # For now, if the console args are requested,
        # return all the kwargs without any specific order.
        return {**super().dict(), **self.additional_kwargs()}


class Config(BaseModel):
    images: Dict[str, ImageConfig]
