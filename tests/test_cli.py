import os
import shutil
import tempfile
from pathlib import Path as Pathlib

import pytest
from typer.testing import CliRunner

from agipack.cli import app
from agipack.constants import AGIPACK_BASENAME, AGIPACK_SAMPLE_FILENAME


@pytest.fixture
def runner():
    return CliRunner()


def test_main(runner):
    result = runner.invoke(app)
    assert result.exit_code == 0


def test_init(runner):
    with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert "Sample `agipack.yaml` file generated." in result.output
        assert os.path.exists("agipack.yaml")


def test_generate(runner):

    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        # Copy the sample config file to the current directory
        shutil.copy(AGIPACK_SAMPLE_FILENAME, AGIPACK_BASENAME)
        result = runner.invoke(app, ["generate"])
        assert result.exit_code == 0

        # Use absolute path for the config file
        result = runner.invoke(app, ["generate", "-c", AGIPACK_SAMPLE_FILENAME])
        assert result.exit_code == 0
        assert Pathlib("Dockerfile").exists()

        # Use absolute path for the config file
        result = runner.invoke(app, ["generate", "-c", AGIPACK_SAMPLE_FILENAME, "-o", "Dockerfile.base"])
        assert result.exit_code == 0
        assert Pathlib("Dockerfile.base").exists()
