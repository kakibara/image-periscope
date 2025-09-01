.PHONY: lint

lint:
	poetry run ruff check .
	poetry run mypy .

.PHONY: test

test:
	poetry run pytest
