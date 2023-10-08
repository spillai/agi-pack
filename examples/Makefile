export DOCKER_BUILDKIT ?= 1
export COMPOSE_DOCKER_CLI_BUILD ?= 1
AGIPACK_VERSION := $(shell agi-pack version)

.DEFAULT_GOAL := help
.PHONY: default
SHELL := /bin/bash

default: help;

help:
	@echo "agi-pack (${AGIPACK_VERSION}): Dockerfile generator for AGI -- nothing more, nothing less."
	@echo ""
	@echo "Usage: make <target>"

agi-base-py38-cpu:
	agi-pack generate \
		-c agibuild.base-cpu.yaml \
		--python 3.8 \
		--output-filename docker/Dockerfile.agi-base-py38-cpu
	docker build -f docker/Dockerfile.agi-base-py38-cpu --target base-cpu -t agi-base-py38-cpu .

agi-base-py38-cu118:
	agi-pack generate \
		-c agibuild.base-cu118.yaml \
		--base nvidia/cuda:11.8.0-base-ubuntu22.04 \
		--python 3.8 \
		--output-filename docker/Dockerfile.agi-base-py38-cu118
	docker build -f docker/Dockerfile.agi-base-py38-cu118 --target base-gpu -t agi-base-py38-cu118 .
