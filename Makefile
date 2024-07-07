# Makefile for HomeLab Manager

.PHONY: all install uninstall clean format lint test unit-test functional-test coverage start stop status help
SCRIPT_NAME = main.py
INSTALL_DIR = $(HOME)/.local/bin
VENV_DIR = venv
PYTHON_VERSION = 3.10
PYTHON_MAJOR_MINOR = 3.10

# ANSI color codes
GREEN = \033[0;32m
YELLOW = \033[1;33m
CYAN = \033[0;36m
RED = \033[0;31m
NC = \033[0m # No Color

all: help

venv: requirements.txt
	@echo "$(YELLOW)Creating virtual environment...$(NC)"
	@python$(PYTHON_MAJOR_MINOR) -m venv $(VENV_DIR)
	@. $(VENV_DIR)/bin/activate && pip install --upgrade pip
	@. $(VENV_DIR)/bin/activate && pip install -r requirements.txt
	@echo "$(GREEN)Virtual environment created and dependencies installed.$(NC)"

install: venv
	@echo "$(YELLOW)Installing HomeLab Manager to $(INSTALL_DIR)$(NC)"
	@mkdir -p $(INSTALL_DIR)
	@cp $(SCRIPT_NAME) $(INSTALL_DIR)/homelab-manager
	@chmod +x $(INSTALL_DIR)/homelab-manager
	@echo "$(GREEN)Installation complete. You can now use 'make' commands to manage your HomeLab.$(NC)"
	@echo "$(YELLOW)Please add $(INSTALL_DIR) to your PATH if it's not already there.$(NC)"

uninstall: clean
	@echo "$(YELLOW)Uninstalling HomeLab Manager from $(INSTALL_DIR)$(NC)"
	@rm -f $(INSTALL_DIR)/homelab-manager
	@echo "$(GREEN)Uninstallation complete.$(NC)"

clean:
	@echo "$(YELLOW)Cleaning up...$(NC)"
	@rm -rf $(VENV_DIR)
	@rm -f *~
	@rm -rf .pytest_cache
	@rm -rf .coverage
	@rm -rf htmlcov
	@echo "$(GREEN)Cleanup complete.$(NC)"

format: venv
	@echo "$(YELLOW)Formatting code...$(NC)"
	@. $(VENV_DIR)/bin/activate && isort homelab_manager/ tests/
	@. $(VENV_DIR)/bin/activate && black homelab_manager/ tests/
	@echo "$(GREEN)Formatting completed.$(NC)"

lint: venv
	@echo "$(YELLOW)Running autopep8 to fix style issues...$(NC)"
	@. $(VENV_DIR)/bin/activate && autopep8 --in-place --aggressive --aggressive --recursive homelab_manager/ tests/
	@echo "$(YELLOW)Running flake8 to check for remaining issues...$(NC)"
	@. $(VENV_DIR)/bin/activate && flake8 homelab_manager/ tests/ || true
	@echo "$(GREEN)Linting completed. Please review any remaining issues manually.$(NC)"

unit-test: venv format lint
	@echo "$(YELLOW)Running unit tests...$(NC)"
	@. $(VENV_DIR)/bin/activate && pytest tests/test_config.py tests/test_service_manager.py -v
	@echo "$(GREEN)Unit tests completed.$(NC)"

functional-test: venv format lint
	@echo "$(YELLOW)Running functional tests...$(NC)"
	@. $(VENV_DIR)/bin/activate && HOMELAB_CONFIG=test_config.json pytest tests/test_functional.py -v
	@echo "$(GREEN)Functional tests completed.$(NC)"

test: unit-test functional-test
	@echo "$(GREEN)All tests completed.$(NC)"

coverage: test
	@echo "$(YELLOW)Running tests with coverage...$(NC)"
	@. $(VENV_DIR)/bin/activate && HOMELAB_CONFIG=test_config.json pytest --cov=homelab_manager --cov-report=term-missing --cov-report=html tests/
	@echo "$(GREEN)Coverage report generated. See htmlcov/index.html for details.$(NC)"

start: venv
	@echo "$(CYAN)Starting all enabled HomeLab services...$(NC)"
	@. $(VENV_DIR)/bin/activate && python $(SCRIPT_NAME) start-all

stop: venv
	@echo "$(CYAN)Stopping all HomeLab services...$(NC)"
	@. $(VENV_DIR)/bin/activate && python $(SCRIPT_NAME) stop-all

status: venv
	@echo "$(CYAN)Checking status of HomeLab services...$(NC)"
	@. $(VENV_DIR)/bin/activate && python $(SCRIPT_NAME) status

help:
	@echo "Available commands:"
	@echo "  $(GREEN)make install$(NC)    - Install the HomeLab Manager"
	@echo "  $(RED)make uninstall$(NC)  - Uninstall the HomeLab Manager"
	@echo "  $(CYAN)make unit-test$(NC)  - Run unit tests"
	@echo "  $(CYAN)make functional-test$(NC) - Run functional tests"
	@echo "  $(CYAN)make test$(NC)       - Run all tests"
	@echo "  $(YELLOW)make coverage$(NC)   - Run tests with coverage report"
	@echo "  $(GREEN)make start$(NC)      - Start all enabled HomeLab services"
	@echo "  $(RED)make stop$(NC)       - Stop all HomeLab services"
	@echo "  $(YELLOW)make status$(NC)     - Check status of all HomeLab services"
	@echo "  $(RED)make clean$(NC)      - Clean up temporary files"
	@echo "  $(CYAN)make help$(NC)       - Show this help message"