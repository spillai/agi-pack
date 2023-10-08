import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from agipack.builder import AGIPack, AGIPackConfig
from agipack.constants import AGIPACK_SAMPLE_FILENAME


@pytest.fixture
def builder(sample_config_filename):
    config = AGIPackConfig.load_yaml(sample_config_filename)
    yield AGIPack(config)


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


def test_builder_cls(test_data_dir):
    # Create an AGIPack instance where the output
    # directory is specified
    with tempfile.TemporaryDirectory() as tmp_dir:
        config = AGIPackConfig.load_yaml(test_data_dir / "agibuild-minimal.yaml")
        builder = AGIPack(config, output_filename=str(Path(tmp_dir) / "Dockerfile"))
        dockerfiles = builder.build_all()
        assert "base-cpu" in dockerfiles
        assert Path(dockerfiles["base-cpu"]).exists()
        assert Path(dockerfiles["base-cpu"]).parent == Path(tmp_dir)


@pytest.mark.skip(reason="Not implemented yet")
def test_builder_cls_with_deps(test_data_dir):
    # Create an AGIPack instance where the output
    # directory is specified
    with tempfile.TemporaryDirectory() as tmp_dir:
        config = AGIPackConfig.load_yaml(test_data_dir / "agibuild-with-deps.yaml")
        builder = AGIPack(config, output_filename=str(Path(tmp_dir) / "Dockerfile"))
        dockerfiles = builder.build_all()
        assert "base-cpu" in dockerfiles
        assert "dev-cpu" in dockerfiles
        assert Path(dockerfiles["base-cpu"]).exists()
        assert Path(dockerfiles["base-cpu"]).parent == Path(tmp_dir)
