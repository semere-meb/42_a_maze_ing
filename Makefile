VENV = .venv


install: $(VENV)

$(VENV): pyproject.toml uv.lock
	pipx install uv
	uv venv --python 3.10
	uv sync

run: $(VENV)
	uv run python src/main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf .mypy__
	rm -rf build/
	rm -rf $(VENV)

lint: $(VENV)
	uv run flake8 .
	uv run mypy . \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

lint-strict: $(VENV)
	uv run flake8 .
	uv run mypy . --strict

debug: $(VENV)
	uv run python -m pdb src/main.py

reset-env:
	rm -rf $(VENV)
	$(MAKE) install

re: clean install

.PHONY: install run clean lint lint-strict debug re reset-env
