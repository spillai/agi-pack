import os
from pathlib import Path

AGIPACK_BASE_DIR = Path(__file__).parent
AGIPACK_BASENAME = "agibuild.yaml"
AGIPACK_TEMPLATE_DIR = AGIPACK_BASE_DIR / "templates"
AGIPACK_DOCKERFILE_TEMPLATE = "Dockerfile.j2"
AGIPACK_SAMPLE_FILENAME = AGIPACK_BASE_DIR / "templates/agibuild.sample.yaml"
AGIPACK_ENV = os.getenv("AGIPACK_ENV", "prod")
