VENV = .venv

run: install
	uv run python src/main.py

install: $(VENV)

$(VENV): pyproject.toml uv.lock
	pipx install uv
	uv venv --python 3.10
	uv sync

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf $(VENV)

lint: $(VENV)
	uv run ruff check src
	uv run flake8 src
	uv run mypy src \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

lint-strict: $(VENV)
	uv run ruff check src
	uv run flake8 src
	uv run mypy src --strict

format:
	uv run ruff format src

debug: $(VENV)
	uv run python -m pdb src/main.py

reset-env:
	rm -rf $(VENV)
	$(MAKE) install

re: clean install

.PHONY: install run clean lint lint-strict debug re reset-env
