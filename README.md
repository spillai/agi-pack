<h1 align="center" style="font-size:64px;font-weight: bold;font-color:black;">📦 agi-pack</h1>
<h4 align="center">
<i>A Dockerfile builder for Machine Learning developers.</i>
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

📦 **`agi-pack`** allows you to define your Dockerfiles using a simple YAML format, and then generate images from them trivially using [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) templates and [Pydantic](https://docs.pydantic.dev/latest/)-based validation. It's a simple tool that aims to simplify the process of building Docker images for machine learning (ML).

## Goals 🎯

- 😇 **Simplicity**: Make it easy to define and build docker images for ML.
- 📦 **Best-practices**: Bring best-practices to building docker images for ML -- good base images, multi-stage builds, minimal image sizes, etc.
- ⚡️ **Fast**: Make it lightning-fast to build and re-build docker images with out-of-the-box caching for apt, conda and pip packages.
- 🧩 **Modular, Re-usable, Composable**: Define `base`, `dev` and `prod` targets with multi-stage builds, and re-use them wherever possible.
- 👩‍💻 **Extensible**: Make the YAML / DSL easily hackable and extensible to support the ML ecosystem, as more libraries, drivers, HW vendors, come into the market.
- ☁️ **Vendor-agnostic**: `agi-pack` is not intended to be built for any specific vendor -- I need this tool for internal purposes, but I decided to build it in the open and keep it simple.

## Installation 📦

```bash
pip install agi-pack
```

For shell completion, you can install them via:
```bash
agi-pack --install-completion <bash|zsh|fish|powershell|pwsh>
```

Go through the [examples](./examples) and the corresponding [examples/generated](./examples/generated) directory to see a few examples of what `agi-pack` can do. If you're interested in checking out a CUDA / CUDNN example, check out [examples/agibuild.base-cu118.yaml](./examples/agibuild.base-cu118.yaml).

## Quickstart 🛠

1. Create a simple YAML configuration file called `agibuild.yaml`. You can use `agi-pack init` to generate a sample configuration file.

    ```bash
    agi-pack init
    ```

2. Edit `agibuild.yaml` to define your custom system and python packages.

    ```yaml
    images:
      sklearn-base:
        base: debian:buster-slim
        system:
        - wget
        - build-essential
        python: "3.8.10"
        pip:
        - loguru
        - typer
        - scikit-learn
    ```

    Let's break this down:
    - `sklearn-base`: name of the target you want to build. Usually, these could be variants like `*-base`, `*-dev`, `*-prod`, `*-test` etc.
    - `base`: base image to build from.
    - `system`: system packages to install via `apt-get install`.
    - `python`: specific python version to install via `miniconda`.
    - `pip`: python packages to install via `pip install`.

3. Generate the Dockerfile using `agi-pack generate`

    ```bash
    agi-pack generate -c agibuild.yaml
    ```

    You should see the following output:

    ```bash
    $ agi-pack generate -c agibuild.yaml
    📦 sklearn-base
    └── 🎉 Successfully generated Dockerfile (target=sklearn-base, filename=Dockerfile).
        └── `docker build -f Dockerfile --target sklearn-base .`
    ```

That's it! Here's the generated [`Dockerfile`](examples/generated/Dockerfile-quickstart) -- use it to run `docker build` and build the image directly.

## Rationale 🤔

Docker has become the standard for building and managing isolated environments for ML. However, any one who has gone down this rabbit-hole knows how broken ML development is, especially when you need to experiment and re-configure your environments constantly. Production is another nightmare -- large docker images (`10GB+`), bloated docker images with model weights that are `~5-10GB` in size, 10+ minute long docker build times, sloppy package management to name just a few.

**What makes Dockerfiles painful?** If you've ever tried to roll your own Dockerfiles with all the best-practices while fully understanding their internals, you'll still find yourself building, and re-building, and re-building these images across a whole host of use-cases. Having to build Dockerfile(s) for `dev`, `prod`, and `test` all turn out to be a nightmare when you add the complexity of hardware targets (CPUs, GPUs, TPUs etc), drivers, python, virtual environments, build and runtime dependencies.

**agi-pack** aims to simplify this by allowing developers to define Dockerfiles in a concise YAML format and then generate them based on your environment needs (i.e. python version, system packages, conda/pip dependencies, GPU drivers etc).

For example, you should be able to easily configure your `dev` environment for local development, and have a separate `prod` environment where you'll only need the runtime dependencies avoiding any bloat.

`agi-pack` hopes to also standardize the base images, so that we can really build on top of giants.

## More Complex Example 📚

Now imagine you want to build a more complex image that has multiple stages, and you want to build a `base` image that has all the basic dependencies, and a `dev` image that has additional build-time dependencies.

```yaml
images:
  base-cpu:
    name: agi
    base: debian:buster-slim
    system:
        - wget
    python: "3.8.10"
    pip:
        - scikit-learn
    run:
        - echo "Hello, world!"

  dev-cpu:
    base: base-cpu
    system:
    - build-essential
```

Once you've defined this `agibuild.yaml`, running `agi-pack generate` will generate the following output:

```bash
$ agi-pack generate -c agibuild.yaml
📦 base-cpu
└── 🎉 Successfully generated Dockerfile (target=base-cpu, filename=Dockerfile).
    └── `docker build -f Dockerfile --target base-cpu .`
📦 dev-cpu
└── 🎉 Successfully generated Dockerfile (target=dev-cpu, filename=Dockerfile).
    └── `docker build -f Dockerfile --target dev-cpu .`
```

As you can see, `agi-pack` will generate a **single** Dockerfile for each of the targets defined in the YAML file. You can then build the individual images from the same Dockerfile using docker targets: `docker build -f Dockerfile --target <target> .` where `<target>` is the name of the image target you want to build.

Here's the corresponding [`Dockerfile`](./examples/generated/Dockerfile-multistage) that was generated.


## Why the name? 🤷‍♂️
`agi-pack` is very much intended to be tongue-in-cheek -- we are soon going to be living in a world full of quasi-AGI agents orchestrated via ML containers. At the very least, `agi-pack` should provide the building blocks for us to build a more modular, re-usable, and distribution-friendly container format for "AGI".

## Inspiration and Attribution 🌟

> **TL;DR** `agi-pack` was inspired by a combination of [Replicate's `cog`](https://github.com/replicate/cog), [Baseten's `truss`](https://github.com/basetenlabs/truss/), [skaffold](https://skaffold.dev/), and [Docker Compose Services](https://docs.docker.com/compose/compose-file/05-services/). I wanted a standalone project without any added cruft/dependencies of vendors and services.

📦 **agi-pack** is simply a weekend project I hacked together, that started with a conversation with [ChatGPT / GPT-4](#chatgpt-prompt).

### ChatGPT Prompt
---

> **Prompt:** I'm building a Dockerfile generator and builder to simplify machine learning infrastructure. I'd like for the Dockerfile to be dynamically generated (using Jinja templates) with the following parametrizations:

```yaml
# Sample YAML file
images:
  base-gpu:
    base: nvidia/cuda:11.8.0-base-ubuntu22.04
    system:
    - gnupg2
    - build-essential
    - git
    python: "3.8.10"
    pip:
    - torch==2.0.1
```
> I'd like for this yaml file to generate a Dockerfile via `agi-pack generate -c <name>.yaml`. You are an expert in Docker and Python programming, how would I implement this builder in Python. Use Jinja2 templating and miniconda python environments wherever possible. I'd like an elegant and concise implementation that I can share on PyPI.

## Contributing 🤝

Contributions are welcome! Please read the [CONTRIBUTING](CONTRIBUTING.md) guide for more information.

## License 📄

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
