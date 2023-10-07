<h1 align="center" style="font-size:64px;font-weight: bold;font-color:black;">agi-pack</h1>
<h4 align="center">
<i>A Dockerfile builder for AGI — nothing more, nothing less.</i>
</h4>

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

Docker has become the de-facto standard for building and managing isolated runtime environments for ML. But it is broken for ML development where you need to experiment and re-configure your environments constantly. Production is another nightmare -- large docker images (`10GB+`), adding `5-10GB` model weights into images (for warm-start purposes), high cache-miss rates for docker images, sloppy package management to name a few.

**More pain** If you've ever tried to roll your own Dockerfiles with best-practices and fully understanding their internals, you'll still find yourself building, and re-building, and re-building these images across a whole host of repositories.

**Even more pain** Having to build Dockerfile(s) for `/dev`, `/prod`, and `test` all turn out to be a nightmare when you add the complexity of hardware targets (CPUs, GPUs, TPUs etc), drivers, python, virtual environments, build and runtime dependencies.

**agi-pack** simplifies this process by allowing developers to define Dockerfiles in a concise YAML format and then generate and build docker images easily. You can choose to build the `Dockerfile` and continue building with `docker`, or use `agi-pack` to build the image directly. `agi-pack` hopes to also standardize the base images, so that we can really build on top of giants.

## Features ✨

- **Simple Configuration**: Define your Docker images using a straightforward YAML format.
- **Dynamic Generation**: Use the power of Jinja2 templating to create Dockerfiles on-the-fly.
- **Sequential and Multi-stage Builds**: Define base images and build dependent images for `/dev`, `/prod`, `/test`.
- **Extensible**: Easily extend and adapt to more complex scenarios.

## Why the name? 🤷‍♂️
`agi-pack` is very much intended to be tongue-in-cheek. It's realization I had that we're soon going to be living in a world of quasi-AGI agents orchestrated via containers. At the very least, `agi-pack` should provide the building blocks for us to build a more modular, re-usable, and distribution-friendly docker images for "AGI".

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

    ```bash
    agi-pack init
    ```

2. Edit `agipack.yaml` to define your custom system and python packages

    ```yaml
    images:
    base-sklearn:
        image: autonomi/agi:latest-base-sklearn
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

## Inspiration and Attribution 🌟

**agi-pack** is simply a weekend project I hacked together, starting with a conversation with ChatGPT / GPT-4 below.
🚨 **Disclaimer: ** More than 90% of this codebase was generated by GPT-4 and [Github Co-Pilot](https://github.com/features/copilot).

    ```
    I'm building a Dockerfile generator and builder to simplify machine learning infrastructure. I'd like for the Dockerfile to be dynamically generated (using Jinja templates) with the following parametrizations:

    # Sample YAML file
    images:
    base-gpu:
        image: autonomi/agi:latest-base-gpu
        base: "nvidia/cuda:11.8.0-base-ubuntu22.04"
        system:
        - "gnupg2"
        - "build-essential"
        - "git"
        python: "3.8.10"
        pip:
        - "torch==2.0.1"

    I'd like for this yaml file to generate a Dockerfile via `agi-pack generate -c <name>.yaml`.

    You are an expert in Docker and Python programming, how would I implement this builder in Python. Use Jinja2 templating and miniconda python environments wherever possible. I'd like an elegant and concise implementation that I can share on PyPI.
    ```

TL;DR `agi-pack` was inspired by a combination of [Replicate's `cog`](https://github.com/replicate/cog), [Baseten's `truss`](https://github.com/basetenlabs/truss/), [skaffold](https://skaffold.dev/), and [Docker Compose Services](https://docs.docker.com/compose/compose-file/05-services/). I wanted a standalone project without any added cruft/dependencies of vendors and services.

## Contributing 🤝

Contributions are welcome! Please read the [CONTRIBUTING](CONTRIBUTING.md) guide for more information.

## License 📄

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
