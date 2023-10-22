import logging
from pathlib import Path

import pytest

from agipack.builder import AGIPack, AGIPackConfig

logger = logging.getLogger(__name__)


EXAMPLES_DIR = Path(__file__).parent.parent / "examples"  # noqa: F405
EXAMPLES = list(EXAMPLES_DIR.glob("*.yaml"))


@pytest.mark.parametrize("filename", EXAMPLES)
def test_parse_yaml(filename):
    logger.info(f"Testing example {filename}")
    try:
        config = AGIPackConfig.load_yaml(filename)
        assert config is not None
    except Exception as e:
        raise Exception(f"Failed to parse {filename}, e={e}")

    basename = filename.stem.replace("agibuild.", "")
    filename = EXAMPLES_DIR / "generated" / f"Dockerfile-{basename}"
    AGIPack(config).render(filename=filename)
