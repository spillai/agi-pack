import logging
import os

import pytest

from agipack.config import AGIPackConfig

logging_level = os.environ.get("AGIPACK_LOGGING_LEVEL", "DEBUG")
logging.basicConfig(level=logging.getLevelName(logging_level))
logger = logging.getLogger(__name__)


def test_configs(test_data_dir):
    configs = [
        test_data_dir / "agibuild-minimal.yaml",
        test_data_dir / "agibuild-with-deps.yaml",
        test_data_dir / "agibuild-no-system.yaml",
        test_data_dir / "agibuild-no-deps.yaml",
        test_data_dir / "agibuild-different-py-versions.yaml",
    ]
    for filename in configs:
        logger.info(f"Testing {filename}")
        config = AGIPackConfig.load_yaml(filename)
        assert config is not None


def test_poorly_formatted_configs(test_data_dir):
    poorly_formatted_configs = [
        test_data_dir / "agibuild-no-base.yaml",
        test_data_dir / "agibuild-malformed-add.yaml",
    ]
    for filename in poorly_formatted_configs:
        with pytest.raises(ValueError):
            AGIPackConfig.load_yaml(filename)
