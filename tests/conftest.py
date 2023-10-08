from pathlib import Path

import pytest

TEST_DIR = Path(__file__).parent  # noqa: F405
TEST_DATA_DIR = Path(__file__).parent / "test_data"  # noqa: F405


@pytest.fixture
def test_data_dir():
    return TEST_DATA_DIR


@pytest.fixture
def test_dir():
    return TEST_DIR


@pytest.fixture
def sample_config_filename():
    from agipack.constants import AGIPACK_SAMPLE_FILENAME

    return AGIPACK_SAMPLE_FILENAME
