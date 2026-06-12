.PHONY: help install dev-install run test lint format clean docs

PYTHON := python3
PIP := pip3
VENV := .venv
VENV_BIN := $(VENV)/bin
PROJECT_NAME := inflation-prediction-system

help:
	@echo "$(PROJECT_NAME) - Makefile commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev-install   - Install dev dependencies"
	@echo "  make run           - Run the inflation prediction pipeline"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters (flake8, mypy)"
	@echo "  make format        - Format code (black, isort)"
	@echo "  make clean         - Remove build artifacts"
	@echo "  make venv          - Create virtual environment"
	@echo "  make docs          - Generate documentation"
	@echo ""

venv:
	$(PYTHON) -m venv $(VENV)
	$(VENV_BIN)/pip install --upgrade pip setuptools wheel

install: venv
	$(VENV_BIN)/pip install -r requirements.txt

dev-install: venv
	$(VENV_BIN)/pip install -r requirements.txt
	$(VENV_BIN)/pip install -e ".[dev,docs]"

run:
	$(VENV_BIN)/python src/inflation_prediction/main_orchestrator.py

run-mock:
	$(VENV_BIN)/python -c "from src.inflation_prediction.main_orchestrator import InflationPredictionOrchestrator; InflationPredictionOrchestrator(llm_backend='mock').execute()"

test:
	$(VENV_BIN)/pytest tests/ -v --cov=src/inflation_prediction

lint:
	$(VENV_BIN)/flake8 src/ tests/ --max-line-length=100
	$(VENV_BIN)/mypy src/inflation_prediction

format:
	$(VENV_BIN)/black src/ tests/
	$(VENV_BIN)/isort src/ tests/

format-check:
	$(VENV_BIN)/black --check src/ tests/
	$(VENV_BIN)/isort --check-only src/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:
	$(VENV_BIN)/sphinx-build -b html docs/ docs/_build/

.DEFAULT_GOAL := help
