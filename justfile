set dotenv-load
set shell := ["bash", "-cu"] # Always use bash so &&, ||, and redirects work predictably

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache build dist src/*.egg-info

sync:
    uv sync --all-extras

format:
    uv run ruff check --select I --fix src
    uv run ruff format src

lint *args: format
    uv run ruff check {{args}} src
    uv run mypy src

outdated:
    uv pip list --outdated

dev:
    uv run uvicorn api:app --reload
