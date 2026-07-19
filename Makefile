# Configuration
PYTHON_BIN ?= python3
VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
UNAME_S := $(shell uname -s)

.PHONY: help venv install install-dev clean run fresh lint check test

help:
	@echo "py_img_scaler Automation Commands:"
	@echo "  make fresh     - Complete reset: cleans, rebuilds venv, and installs packages"
	@echo "  make venv      - Create a clean local virtual environment"
	@echo "  make install   - Install production dependencies"
	@echo "  make install-dev- Install all dependencies (including dev tools)"
	@echo "  make run       - Execute py_img_scaler main loop"
	@echo "  make clean     - Destroy virtual environment and cache"
	@echo "  make lint      - Auto-format and fix lint issues"
	@echo "  make check     - Check formatting/linting without modifying files"
	@echo "  make test      - Run unit tests via pytest"

fresh: clean venv install-dev
	@echo "Environment successfully rebuilt on $(UNAME_S)!"

venv:
	@echo "Creating virtual environment..."
	$(PYTHON_BIN) -m venv $(VENV_DIR)

install: venv
	@echo "Upgrading build tools..."
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	@echo "Installing hardware-accelerated dependencies..."
ifeq ($(UNAME_S), Darwin)
	$(PYTHON) -m pip install torch torchvision torchaudio
else
	$(PYTHON) -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm7.2
endif
	@echo "Installing project in editable mode..."
	$(PYTHON) -m pip install -e .

# Installs dev extras defined in pyproject.toml
install-dev: install
	@echo "Installing development dependencies..."
	$(PYTHON) -m pip install -e ".[dev]"

run:
	$(PYTHON) main.py

clean:
	rm -rf $(VENV_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	$(PYTHON) -m black .
	$(PYTHON) -m ruff check --fix .

check:
	$(PYTHON) -m black --check .
	$(PYTHON) -m ruff check .
	$(PYTHON) -m mypy .

test:
	$(PYTHON) -m pytest tests/