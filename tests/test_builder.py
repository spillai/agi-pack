import logging
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from agipack.builder import AGIPack, AGIPackConfig
from agipack.constants import AGIPACK_SAMPLE_FILENAME

logger = logging.getLogger(__name__)


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
        dockerfiles = builder.render()
        assert "base-cpu" in dockerfiles
        assert dockerfiles["base-cpu"] == "Dockerfile"
        assert Path(dockerfiles["base-cpu"]).exists()

    # Use hadolint within docker to lint/check the generated Dockerfile
    cmd = "docker pull hadolint/hadolint && "
    cmd += f"docker run --pull=always --rm -i hadolint/hadolint < {dockerfiles['base-cpu']}"
    logger.info("Linting with hadolint")
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        shell=True,
    )
    for line in iter(process.stdout.readline, ""):
        logger.info(line.rstrip())


def test_builder_cls(test_data_dir):
    # Create an AGIPack instance where the output
    # directory is specified
    config = AGIPackConfig.load_yaml(test_data_dir / "agibuild-minimal.yaml")
    with tempfile.TemporaryDirectory() as tmp_dir:
        builder = AGIPack(config, output_filename=str(Path(tmp_dir) / "Dockerfile"))
        dockerfiles = builder.render()
        assert "base-cpu" in dockerfiles
        assert Path(dockerfiles["base-cpu"]).exists()
        assert Path(dockerfiles["base-cpu"]).parent == Path(tmp_dir)


def test_builder_cls_with_deps(test_data_dir):
    # Create an AGIPack instance where the output
    # directory is specified
    config = AGIPackConfig.load_yaml(test_data_dir / "agibuild-with-deps.yaml")
    with tempfile.TemporaryDirectory() as tmp_dir:
        builder = AGIPack(config, output_filename=str(Path(tmp_dir) / "Dockerfile"))
        dockerfiles = builder.render()
        assert "base-cpu" in dockerfiles
        assert "dev-cpu" in dockerfiles
        assert Path(dockerfiles["base-cpu"]).exists()
        assert Path(dockerfiles["base-cpu"]).parent == Path(tmp_dir)
