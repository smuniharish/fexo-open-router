.PHONY: install start update format type-lint lint pc-install check

install:
	poetry install

start:
	${DOTENV_CMD} poetry run python main.py
start-dev:
	$(MAKE) start ENV=development

start-staging:
	$(MAKE) start ENV=staging

start-production:
	$(MAKE) start ENV=production

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