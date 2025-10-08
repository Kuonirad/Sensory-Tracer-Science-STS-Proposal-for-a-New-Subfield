# Makefile for Sensory Tracer Science (STS)
# Scientific-grade repository management and quality assurance

.PHONY: help install test lint format docs clean validate benchmark publish

# Default target
help:
	@echo "Sensory Tracer Science (STS) - Scientific Repository Management"
	@echo "=============================================================="
	@echo ""
	@echo "Development Commands:"
	@echo "  install     Install package and dependencies"
	@echo "  install-dev Install with development dependencies"
	@echo "  test        Run comprehensive test suite"
	@echo "  lint        Run code quality checks"
	@echo "  format      Format code with black and isort"
	@echo "  typecheck   Run static type checking with mypy"
	@echo ""
	@echo "Validation Commands:"
	@echo "  validate    Run STS framework validation"
	@echo "  codata      Validate CODATA 2022 constants"
	@echo "  landauer    Validate Landauer compliance"
	@echo "  physics     Validate physical consistency"
	@echo ""
	@echo "Documentation Commands:"
	@echo "  docs        Build documentation"
	@echo "  docs-serve  Serve documentation locally"
	@echo "  docs-clean  Clean documentation build"
	@echo ""
	@echo "Quality Assurance Commands:"
	@echo "  benchmark   Run performance benchmarks"
	@echo "  coverage    Generate test coverage report"
	@echo "  security    Run security vulnerability scan"
	@echo ""
	@echo "Release Commands:"
	@echo "  clean       Clean build artifacts"
	@echo "  build       Build distribution packages"
	@echo "  publish     Publish to PyPI (requires authentication)"
	@echo ""

# Installation
install:
	pip install -e .

install-dev:
	pip install -e .[dev,docs,jupyter]
	pre-commit install

# Testing
test:
	pytest -v --cov=sensory_tracer_science --cov-report=html --cov-report=term-missing

test-fast:
	pytest -v -x --ff

test-scientific:
	pytest -v tests/test_scientific_standards.py

# Code Quality
lint: 
	flake8 sensory_tracer_science
	pydocstyle sensory_tracer_science --convention=google

format:
	black sensory_tracer_science tests
	isort sensory_tracer_science tests

typecheck:
	mypy sensory_tracer_science --ignore-missing-imports

# STS Framework Validation
validate:
	@echo "🔬 STS Framework Validation"
	@echo "=========================="
	python validate_augmented_framework.py

codata:
	@echo "📊 CODATA 2022 Constants Validation"
	@echo "==================================="
	@python -c "from sensory_tracer_science.core.sts_constants import *; \
	assert abs(K_B - 1.380649e-23) < 1e-30, 'Boltzmann constant incorrect'; \
	assert abs(HBAR - 1.054571817e-34) < 1e-40, 'Planck constant incorrect'; \
	assert abs(C_VACUUM - 299792458.0) < 1e-6, 'Speed of light incorrect'; \
	print('✅ All CODATA 2022 constants validated')"

landauer:
	@echo "⚡ Landauer Compliance Validation"
	@echo "================================"
	@python -c "from sensory_tracer_science.core.sts_constants import STSLimits; \
	landauer = STSLimits.landauer_limit(310.0); \
	assert landauer > 0, 'Landauer limit must be positive'; \
	print(f'✅ Landauer limit at 310K: {landauer:.2e} J/bit')"

physics:
	@echo "🧮 Physical Consistency Validation"  
	@echo "=================================="
	@python -c "from sensory_tracer_science.core.sts_constants import validate_augmented_physics; \
	results = validate_augmented_physics(); \
	assert results['augmented_validation_status'] == 'PASSED', 'Physics validation failed'; \
	print('✅ All physics equations validated')"

# Documentation
docs:
	cd docs && make html

docs-serve:
	cd docs/_build/html && python -m http.server 8000

docs-clean:
	cd docs && make clean

# Quality Assurance
benchmark:
	@echo "🏃 Performance Benchmarks"
	@echo "========================"
	python -m pytest --benchmark-only --benchmark-sort=mean

coverage:
	pytest --cov=sensory_tracer_science --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

security:
	bandit -r sensory_tracer_science/
	safety check

# Repository Management
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

publish: build
	python -m twine upload dist/*

# Continuous Integration Simulation
ci: install-dev lint typecheck test validate docs
	@echo "🎉 All CI checks passed!"

# Scientific Validation Suite
scientific-validation: codata landauer physics test-scientific
	@echo "🔬 Scientific validation complete!"
	@echo ""
	@echo "Framework Status:"
	@echo "  ✅ CODATA 2022 constants validated"
	@echo "  ✅ Landauer compliance verified"  
	@echo "  ✅ Physical consistency confirmed"
	@echo "  ✅ Scientific standards met"
	@echo ""
	@echo "🧬 Ready for experimental validation!"

# Pre-commit hooks
pre-commit:
	pre-commit run --all-files

# Full quality check
quality: format lint typecheck security coverage
	@echo "✅ Quality assurance complete!"

# Release preparation
prepare-release: quality scientific-validation docs
	@echo "📦 Release preparation complete!"
	@echo "Ready to build and publish."