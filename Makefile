# Define the python interpreter to use for environment creation
PYTHON_BIN ?= python3.12
VENV_DIR = .venv

# Check OS to handle activate path variance if needed later
UNAME_S := $(shell uname -s)

.PHONY: help venv install clean run fresh

help:
	@echo "PyImgScaler Automation Commands:"
	@echo "  make fresh     - Complete reset: cleans, rebuilds venv, and installs packages"
	@echo "  make venv      - Create a clean local virtual environment using $(PYTHON_BIN)"
	@echo "  make install   - Upgrade core tooling and install packages with correct build flags"
	@echo "  make run       - Execute PyImgScaler main loop"
	@echo "  make clean     - Destroy virtual environment and cached bytecodes"

fresh: clean venv install
	@echo "========================================================================"
	@echo " PyImgScaler environment successfully rebuilt from scratch on $(UNAME_S)!"
	@echo "========================================================================"

venv:
	@echo "Creating virtual environment..."
	$(PYTHON_BIN) -m venv $(VENV_DIR)
	@echo "Environment created at ./$(VENV_DIR)"

install:
	@echo "Upgrading pip, setuptools, and wheel inside the venv..."
	$(VENV_DIR)/bin/python -m pip install --upgrade pip setuptools wheel
	@echo "Installing system-agnostic requirements without build isolation..."
	$(VENV_DIR)/bin/python -m pip install -r requirements.txt --no-build-isolation
	@echo "Dependencies successfully configured."

run:
	$(VENV_DIR)/bin/python main.py

clean:
	@echo "Cleaning up old environment and cache stores..."
	rm -rf $(VENV_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleanup complete."