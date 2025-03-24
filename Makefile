.PHONY: install start update format type-lint lint pc-install check

install:
	poetry install

start:
	poetry run python main.py

update:
	poetry update

format:
	poetry run ruff format

type-lint:
	poetry run mypy .

lint:
	poetry run ruff check

pc-install:
	poetry run pre-commit install

check: format lint type-lint