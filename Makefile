SRC = a_maze_ing.py \
	generator.py \
	parser.py \
	utils.py

VENV = .venv

run: install
	uv run ./a_maze_ing.py config.txt

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
	uv run ruff check $(SRC)
	uv run flake8 $(SRC)
	uv run mypy $(SRC) \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

lint-strict: $(VENV)
	uv run ruff check $(SRC)
	uv run flake8 $(SRC)
	uv run mypy $(SRC) --strict

format:
	uv run ruff format $(SRC)

debug: $(VENV)
	uv run python -m pdb $(SRC)/a_maze_ing.py

reset-env:
	rm -rf $(VENV)
	$(MAKE) install

re: clean install

.PHONY: install run clean lint lint-strict debug re reset-env
