import logging
import subprocess
from pathlib import Path
from typing import Dict

from jinja2 import Environment, FileSystemLoader

from agipack.commands import AGIPackConfig, ImageConfig
from agipack.constants import AGIPACK_DOCKERFILE_TEMPLATE, AGIPACK_TEMPLATE_DIR

logger = logging.getLogger(__name__)


class AGIPack:
    """
    AGIPack: A Dockerfile generator and builder for Machine Learning Infrastructure.

    AGIPack provides a streamlined approach to generating and building Docker images
    tailored for machine learning applications. By leveraging a YAML configuration,
    users can define multiple Docker images with varying configurations, dependencies,
    and commands. This abstracts away the complexities of writing Dockerfiles manually
    and ensures a consistent, reproducible and cache-optimized build process.

    Key Features:
    - **YAML Configuration**: Define Docker images using a simple and intuitive YAML format.
    - **Template-Based Generation**: Uses Jinja2 templates to generate Dockerfiles dynamically.
    - **Custom Commands**: Offers pre-run and post-run commands for custom setup and cleanup tasks.

    Rationale:
        Building Docker images for machine learning can be a repetitive and error-prone task.
        Different projects might require different dependencies, system packages, or configurations.
        AGIPack simplifies this process by allowing users to define all their requirements in a
        structured YAML file. This not only makes the process more efficient but also ensures that
        the Docker images are consistent and reproducible.

    Usage Example:
        ```python
        # Create an AGIPack instance
        builder = AGIPack(config_path="agibuild.yaml")

        # Generate Dockerfiles and build images
        builder.generate_all()
        ```

    Args:
        config (AGIPackConfig): AGIPack configuration.
        output_directory (str): Output directory for the generated Dockerfiles.

    TL;DR - Yet another DSL for building machine-learning Dockerfiles.
    """

    def __init__(self, config: AGIPackConfig, output_filename: str = "Dockerfile"):
        """Initialize the AGIPack instance."""
        self.config = config
        self.output_filename = output_filename
        self.template_env = Environment(loader=FileSystemLoader(searchpath=AGIPACK_TEMPLATE_DIR))

    def generate_dockerfile(self, target: str, image_config: ImageConfig) -> str:
        """Generates a Dockerfile for the given target image.

        Args:
            target (str): Target image name.
            image_config (ImageConfig): Image configuration.
        """
        template = self.template_env.get_template(AGIPACK_DOCKERFILE_TEMPLATE)
        image_dict = image_config.model_dump()
        image_dict["target"] = target
        content = template.render(image_dict)

        # Write the Dockerfile to the specified output filename
        if not Path(self.output_filename).parent.exists():
            Path(self.output_filename).parent.mkdir(parents=True)
        try:
            with open(str(Path(self.output_filename).absolute()), "w") as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Error writing Dockerfile to {self.output_filename}: {e}")
            raise Exception(f"Error writing Dockerfile to {self.output_filename}: {e}")
        return self.output_filename

    def build_image(self, target: str, tag: str, filename: str) -> None:
        """Builds a Docker image using the generated Dockerfile.

        Args:
            target (str): Target image name.
            tag (str): Tag for the Docker image.
            filename (str): Path to the generated Dockerfile.
        """
        process = subprocess.Popen(
            ["docker", "build", "-f", filename, "--target", target, "-t", tag, "."],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        for line in iter(process.stdout.readline, ""):
            print(line, end="")
        process.wait()

    def build_all(self) -> Dict[str, str]:
        """Generates Dockerfiles and builds images for all the images defined in the YAML configuration."""
        dockerfiles = {}
        for image_name, image_config in self.config.images.items():
            logger.info(f"📦 Generating Dockerfile [{image_name}]")
            filename = self.generate_dockerfile(image_name, image_config)
            dockerfiles[image_name] = filename
        return dockerfiles
