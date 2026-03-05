install:
	uv venv --python 3.10
	uv sync

run: install
	pip install uv
	uv run python src/main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf .mypy__
	rm -rf build/
	rm -rf .venv

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict

debug:
	uv run python -m pdb src/main.py

reset-env:
	rm -rf .venv
	pip install uv
	uv venv --python 3.10
	uv sync

re: clean install

.PHONY: install run clean lint lint-strict debug re reset-env
