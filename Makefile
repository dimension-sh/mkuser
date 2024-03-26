poetry:
	python3 -m pip install poetry

tests: poetry
	python3 -m poetry run pytest

lint: poetry
	python3 -m poetry run ruff check --output-format=github --select=E9,F63,F7,F82 --target-version=py39 .
	python3 -m poetry run ruff check --output-format=github --target-version=py39 .
