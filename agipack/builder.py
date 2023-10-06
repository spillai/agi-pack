import logging
import subprocess

from jinja2 import Environment, FileSystemLoader

from agipack.commands import AGIPackConfig, ImageConfig
from agipack.constants import AGI_BUILD_FILENAME, AGI_BUILD_TEMPLATE_DIR

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
        builder = AGIPack(config_path="agipack.yaml")

        # Generate Dockerfiles and build images
        builder.generate_all()
        ```

    Args:
        config_path (str): Path to the YAML configuration file.

    TL;DR - Yet another DSL for building machine-learning Dockerfiles.
    """

    def __init__(self, config_path: str = AGI_BUILD_FILENAME, **kwargs):
        self.config = AGIPackConfig.load_yaml(config_path)
        self.template_env = Environment(loader=FileSystemLoader(searchpath=AGI_BUILD_TEMPLATE_DIR))

    def generate_dockerfile(self, target: str, image_config: ImageConfig) -> str:
        """Generates a Dockerfile for the given target image.

        Args:
            target (str): Target image name.
            image_config (ImageConfig): Image configuration.
        """
        template = self.template_env.get_template("Dockerfile.j2")
        image_dict = image_config.dict()
        image_dict["target"] = target
        content = template.render(image_dict)

        filename = f"Dockerfile.{target}"
        with open(filename, "w") as f:
            f.write(content)
        return filename

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

    def build_all(self):
        """Generates Dockerfiles and builds images for all the images defined in the YAML configuration."""
        for image_name, image_config in self.config.images.items():
            logger.info(f"📦 Generating Dockerfile [{image_name}]")
            filename = self.generate_dockerfile(image_name, image_config)
            print(f"📦 Generated {filename} [{image_name}]")
            print(f"📦 Build `{image_name}`: `docker build -f {filename} --target {image_name} .`")