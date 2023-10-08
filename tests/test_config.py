import pytest

from agipack.config import AGIPackConfig


def test_configs(test_data_dir):
    configs = [
        test_data_dir / "agibuild-minimal.yaml",
        test_data_dir / "agibuild-with-deps.yaml",
    ]
    for filename in configs:
        config = AGIPackConfig.load_yaml(filename)
        assert config is not None


def test_poorly_formatted_configs(test_data_dir):
    poorly_formatted_configs = [
        test_data_dir / "agibuild-no-base.yaml",
        test_data_dir / "agibuild-different-py-versions.yaml",
    ]
    for filename in poorly_formatted_configs:
        with pytest.raises(ValueError):
            AGIPackConfig.load_yaml(filename)
