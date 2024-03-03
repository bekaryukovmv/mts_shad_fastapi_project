flake8-check:
	flake8 --config=.flake8

black-check:
	black . --config=pyproject.toml --check .

isort-check:
	isort . --settings-path=pyproject.toml --diff --check  --skip=.venv

black:
	black . --config pyproject.toml

isort:
	isort . --settings-path=pyproject.toml --skip=.venv

linters-check:
	make isort-check; make black-check; make flake8-check

linters:
	make isort; make black; make flake8-check

pytest:
	pytest -s -vv -x -c=src/pytest.ini src/tests

install_reqs:
	poetry install --no-root --with dev && poetry shell

tests:
	make isort-check; make black-check; make flake8-check; make pytest

up_compose:
	docker-compose -f docker-compose.yml up -d
down_compose:
	docker-compose -f docker-compose.yml down
