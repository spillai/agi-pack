from pathlib import Path

AGIPACK_BASE_DIR = Path(__file__).parent
AGIPACK_BASENAME = "agipack.yaml"
AGIPACK_TEMPLATE_DIR = AGIPACK_BASE_DIR / "templates"
AGIPACK_DOCKERFILE_TEMPLATE = "Dockerfile.j2"
AGIPACK_SAMPLE_FILENAME = AGIPACK_BASE_DIR / "templates/agipack.sample.yaml"
