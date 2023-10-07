import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from agipack.builder import AGIPack, AGIPackConfig
from agipack.constants import AGIPACK_BASENAME, AGIPACK_SAMPLE_FILENAME

SAMPLE_CONFIG = """
images:
  base-cpu:
    system:
      - wget
    python: 3.8.10
    pip:
      - scikit-learn
    run:
      - echo "Hello, world!"
"""


@pytest.fixture(scope="module")
def sample_config_filename():
    with tempfile.TemporaryDirectory() as tmp_dir:
        filename = f"{tmp_dir}/{AGIPACK_BASENAME}"
        with open(str(filename), "w") as f:
            f.write(SAMPLE_CONFIG)
        yield filename


@pytest.fixture(scope="module")
def builder(sample_config_filename):
    yield AGIPack(sample_config_filename)


def test_parse_yaml(sample_config_filename):
    config = AGIPackConfig.load_yaml(AGIPACK_SAMPLE_FILENAME)
    assert config is not None

    config = AGIPackConfig.load_yaml(sample_config_filename)
    assert config is not None


def test_build_all(builder):
    with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)
        dockerfiles = builder.build_all()
        assert "base-cpu" in dockerfiles
        assert dockerfiles["base-cpu"] == "Dockerfile"
        assert Path(dockerfiles["base-cpu"]).exists()

    # Use hadolint within docker to lint/check the generated Dockerfile
    cmd = f"docker run --rm -i hadolint/hadolint < {dockerfiles['base-cpu']}"
    print("Linting with hadolint")
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        shell=True,
    )
    for line in iter(process.stdout.readline, ""):
        print(line, end="")


def test_builder_cls(sample_config_filename):
    # Create an AGIPack instance where the output
    # directory is specified
    with tempfile.TemporaryDirectory() as tmp_dir:
        builder = AGIPack(sample_config_filename, output_filename=str(Path(tmp_dir) / "Dockerfile"))
        dockerfiles = builder.build_all()
        assert "base-cpu" in dockerfiles
        assert Path(dockerfiles["base-cpu"]).exists()
        assert Path(dockerfiles["base-cpu"]).parent == Path(tmp_dir)
