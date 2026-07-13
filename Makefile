# Define the python interpreter to use for environment creation
PYTHON_BIN ?= python
VENV_DIR = .venv

# Check OS to handle platform-specific installation logic
UNAME_S := $(shell uname -s)

.PHONY: help venv install clean run fresh lint check test

help:
	@echo "py_img_scaler Automation Commands:"
	@echo "  make fresh     - Complete reset: cleans, rebuilds venv, and installs packages"
	@echo "  make venv      - Create a clean local virtual environment using $(PYTHON_BIN)"
	@echo "  make install   - Upgrade core tooling and install platform-specific packages"
	@echo "  make run       - Execute py_img_scaler main loop"
	@echo "  make clean     - Destroy virtual environment and cached bytecodes"
	@echo "  make lint      - Runs, Black, Ruff, and MyPy checks"
	@echo "  make check      - Runs, Black, Ruff, and MyPy checks"
	@echo "  make test      - Run all unit tests inside the tests directory"

fresh: clean venv install
	@echo "========================================================================"
	@echo " py_img_scaler environment successfully rebuilt from scratch on $(UNAME_S)!"
	@echo "========================================================================"

venv:
	@echo "Creating virtual environment..."
	$(PYTHON_BIN) -m venv $(VENV_DIR)
	@echo "Environment created at ./$(VENV_DIR)"

install:
	@echo "Upgrading pip, setuptools, and wheel inside the venv..."
	$(VENV_DIR)/bin/python -m pip install --upgrade pip setuptools wheel
ifeq ($(UNAME_S), Darwin)
	@echo "Detected macOS. Installing standard PyTorch (MPS support is native)..."
	$(VENV_DIR)/bin/python -m pip install torch torchvision torchaudio
else
	@echo "Detected Linux. Installing AMD ROCm PyTorch binaries..."
	$(VENV_DIR)/bin/python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm7.2
endif
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


lint:
	@echo "Applying formatting rules and auto-fixing lint issues..."
	.venv/bin/black .
	.venv/bin/ruff check --fix .
	.venv/bin/mypy .


check:
	@echo "Check formatting stats only..."
	.venv/bin/black --check .
	.venv/bin/ruff check .
	.venv/bin/mypy .

test:
	@echo "Executing automated unittest suite suite..."
	$(VENV_DIR)/bin/python -m unittest discover -s tests -p "test_*.py" -v