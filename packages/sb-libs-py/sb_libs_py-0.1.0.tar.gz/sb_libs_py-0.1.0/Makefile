.PHONY: help install install-dev test test-cov coverage-html coverage-xml lint format typecheck build clean docs pre-commit-install pre-commit-run

help:
	@echo "Available commands:"
	@echo "  install           - Install package in development mode"
	@echo "  install-dev       - Install package with development dependencies"
	@echo "  test              - Run tests"
	@echo "  test-cov          - Run tests with coverage (terminal + HTML + XML)"
	@echo "  coverage-html     - Generate HTML coverage report"
	@echo "  coverage-xml      - Generate XML coverage report (same as CI)"
	@echo "  lint              - Run ruff linter"
	@echo "  format            - Format code with ruff"
	@echo "  typecheck         - Run mypy type checker"
	@echo "  build             - Build package"
	@echo "  clean             - Clean build artifacts"
	@echo "  docs              - Build documentation"
	@echo "  pre-commit-install - Install pre-commit hooks"
	@echo "  pre-commit-run     - Run pre-commit on all files"

install:
	uv sync

install-dev:
	uv sync --dev --all-extras

test:
	uv run pytest

# 커버리지와 함께 테스트 실행
test-cov:
	uv run pytest --cov=src/sb_libs --cov-report=term-missing --cov-report=html --cov-report=xml

# 커버리지 리포트 HTML 열기 (브라우저)
coverage-html:
	uv run pytest --cov=src/sb_libs --cov-report=html
	@echo "Coverage report generated at htmlcov/index.html"
	@echo "Open with: xdg-open htmlcov/index.html (Linux) or open htmlcov/index.html (macOS)"

# 커버리지 XML 생성 (CI용과 동일)
coverage-xml:
	uv run pytest --cov=src/sb_libs --cov-report=xml
	@echo "Coverage XML report generated at coverage.xml"

lint:
	uv run ruff check .

format:
	uv run ruff format .

# 현재 (너무 관대함)
typecheck:
	uv run mypy src/ --ignore-missing-imports --no-strict-optional --allow-untyped-defs --disable-error-code=attr-defined --disable-error-code=operator --disable-error-code=var-annotated

# 개선안 (더 엄격함)
typecheck:
	uv run mypy src/ --ignore-missing-imports

typecheck-strict:
	uv run mypy src/ --strict --ignore-missing-imports

typecheck-tests:
	uv run mypy tests/ --ignore-missing-imports

# 타입 힌트 추가 도움
typecheck-html:
	uv run mypy src/ --html-report mypy-report --ignore-missing-imports

# 점진적 타입 검사 (새 파일만)
typecheck-new:
	uv run mypy src/ --ignore-missing-imports --disallow-untyped-defs

# 테스트 파일 타입 검사
typecheck-tests:
	uv run mypy tests/ --ignore-missing-imports

# 전체 프로젝트 타입 검사
typecheck-all:
	uv run mypy src/ tests/ --ignore-missing-imports

build:
	uv run python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:
	cd docs && sphinx-build -b html . _build

pre-commit-install:
	uv run pre-commit install

pre-commit-run:
	uv run pre-commit run --all-files

# 개발 시 사용할 통합 검사
check-all: lint format typecheck test
