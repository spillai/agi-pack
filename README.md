<h1 align="center" style="font-size:54px;font-weight: bold;font-color:black;">agi-pack</h1>
<h4 align="center">
<i>A Dockerfile builder for AGI — nothing more, nothing less.</i>
</h4>

<p align="center">
<a href="https://spillai.github.io/agi-pack/"><b>Docs</b></a> |  <a href="https://discord.gg/QAGgvTuvgg"><b>Discord</b></a>
</p>

<p align="center">
<a href="https://pypi.org/project/agi-pack/">
    <img alt="PyPi Version" src="https://badge.fury.io/py/agi-pack.svg">
</a>
<a href="https://pypi.org/project/agi-pack/">
    <img alt="PyPi Version" src="https://img.shields.io/pypi/pyversions/agi-pack">
</a>
<a href="https://pypi.org/project/agi-pack/">
    <img alt="PyPi Downloads" src="https://img.shields.io/pypi/dm/agi-pack">
</a>

</p>

## Rationale 🤔

Docker has become the de-facto standard for building and managing isolated runtime environments for ML. But it is broken for ML development where you need to experiment and re-configure your environments constantly. Production is another nightmare -- large docker images (`10GB+`), including `5-10GB` model weights into images (for warm-start purposes), high cache-miss rates for docker images, sloppy package management to name a few.

That said, if you've ever tried to roll your own Dockerfiles with best-practices and fully understanding their internals, you'll still find yourself building, and re-building, and re-building these images across a whole host of repositories.

Having to build Dockerfile(s) for `/dev`, `/prod`, and `test` all turn out to be a nightmare when you add the complexity of hardware targets (CPUs, GPUs, TPUs etc), drivers, python, virtual environments, build and runtime dependencies.

**agi-pack** simplifies this process by allowing developers to define Dockerfiles in a concise YAML format and then generate and build docker images easily. You can choose to build the `Dockerfile` and continue building with `docker`, or use `agi-pack` to build the image directly. `agi-pack` hopes to also standardize the base images, so that we can really build on top of giants.

**Why the name?** Bare with me here because this was a weekend project. `agi-pack` is an amusing realization I had that we're soon going to be living in a world of AI/quasi-AGI agents packed into containers. `agi-pack` aims to be the building blocks/`pack`s for us to build more modular, re-usable and composable agents.

## Features ✨

- **Simple Configuration**: Define your Docker images using a straightforward YAML format.
- **Dynamic Generation**: Use the power of Jinja2 templating to create Dockerfiles on-the-fly.
- **Sequential Builds**: Define base images and build dependent images in sequence.
- **Extensible**: Easily extend and adapt to more complex scenarios.

## Inspiration 🌟

**agi-pack** is inspired by a combination of [Replicate's `cog`](https://github.com/replicate/cog), [Baseten's `truss`](https://github.com/basetenlabs/truss/), [skaffold](https://skaffold.dev/), [Modal](https://modal.com/), and [Docker Compose Services](https://docs.docker.com/compose/compose-file/05-services/).

## Installation 📦

```bash
pip install git+hhttps://github.com/spillai/agi-pack.git
```

For shell completion, you can install them via:
```bash
agi-pack --install-completion <bash|zsh|fish|powershell|pwsh>
```

## Usage 🛠

1. Create a simple YAML configuration file called `agipack.yaml` via `agi-pack init`:

`agi-pack init`

2. Edit `agipack.yaml` to define your custom system and python packages

```yaml
images:
  base-sklearn:
    name: agi
    base: python:3.8.10-slim
    system:
    - wget
    - build-essential
    python: 3.8.10
    pip:
    - loguru
    - typer
    - scikit-learn
```

3. Generate the Dockerfile using `agi-pack generate`

```bash
agi-pack generate -c agipack.yaml
```

That's it! You can now build the generated Dockerfile using `docker build` or use `agi-pack build` to build the image directly.

## Contributing 🤝

Contributions are welcome! Please read the [CONTRIBUTING](CONTRIBUTING.md) guide for more information.

## License 📄

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Remember to create a `CONTRIBUTING.md` file if you mention it in the README. This file typically contains guidelines for those who want to contribute to the project.

Also, make sure to replace `yourusername` with your actual GitHub username in the installation section.

This README should give your project a professional look and provide all the necessary information for someone interested in using or contributing to `agipack`.
