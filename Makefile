VENV := .venv
PROJECT := billing
IMAGE_NAME := reco_service
CONTAINER_NAME := reco_service

# Prepare
.venv:
	poetry install --no-root
	poetry check

setup: .venv

# Clean
clean:
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf $(VENV)

# Format
isort_fix: .venv
	poetry run isort $(PROJECT)

black_fix:
	poetry run black $(PROJECT)

format: isort_fix black_fix

# Lint
isort: .venv
	poetry run isort --check $(PROJECT)

.black:
	poetry run black --check --diff $(PROJECT)

flake: .venv
	poetry run flake8 $(PROJECT)

mypy: .venv
	poetry run mypy $(PROJECT)

pylint: .venv
	poetry run pylint $(PROJECT)

lint: isort flake mypy pylint

# Docker
build:
	docker build . -t $(IMAGE_NAME)

run: build
	docker run -p 8080:8080 --name $(CONTAINER_NAME) $(IMAGE_NAME)

# All
all: setup format lint

.DEFAULT_GOAL = all