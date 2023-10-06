import logging

import yaml
from jinja2 import Environment, FileSystemLoader

from agibuilder.commands import Config, ImageConfig
from agibuilder.constants import AGI_BUILD_FILENAME, AGI_BUILD_TEMPLATE_DIR

logger = logging.getLogger(__name__)


class AGIBuilder:
    """
    AGIBuilder: A Dockerfile generator and builder for Machine Learning Infrastructure.

    AGIBuilder provides a streamlined approach to generating and building Docker images
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
        AGIBuilder simplifies this process by allowing users to define all their requirements in a
        structured YAML file. This not only makes the process more efficient but also ensures that
        the Docker images are consistent and reproducible.

    Usage Example:
        ```python
        # Create an AGIBuilder instance
        builder = AGIBuilder(config_path="agibuild.yaml")

        # Generate Dockerfiles and build images
        builder.generate_all()
        ```

    Args:
        config_path (str): Path to the YAML configuration file.

    TL;DR - Yet another DSL for building machine-learning Dockerfiles.
    """

    def __init__(self, config_path: str = AGI_BUILD_FILENAME, **kwargs):
        self.config = self.load_yaml(config_path)
        self.template_env = Environment(loader=FileSystemLoader(searchpath=AGI_BUILD_TEMPLATE_DIR))

    def load_yaml(self, yaml_file: str) -> Config:
        with open(yaml_file, "r") as file:
            data = yaml.safe_load(file)
        return Config(**data)

    def save_yaml(self, yaml_file: str) -> None:
        with open(yaml_file, "w") as file:
            yaml.safe_dump(self.config.dict(), file, sort_keys=False)

    def generate_dockerfile(self, image_config: ImageConfig) -> str:
        template = self.template_env.get_template("Dockerfile.j2")
        return template.render(image_config.dict())

    def build_image(self, dockerfile_content: str, tag: str) -> None:
        with open("Dockerfile", "w") as file:
            file.write(dockerfile_content)

        # process = subprocess.Popen(
        #     ["docker", "build", "-t", tag, "."],
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.STDOUT,
        #     universal_newlines=True,
        # )
        # for line in iter(process.stdout.readline, ""):
        #     print(line, end="")
        # process.wait()

    def generate_all(self):
        for image_name, image_config in self.config.images.items():
            logger.info(f"📦 Generating Dockerfile [{image_name}]")
            dockerfile_content = self.generate_dockerfile(image_config)
            print(f"📦 Generated Dockerfile [{image_name}]")
            self.build_image(dockerfile_content, image_name)
