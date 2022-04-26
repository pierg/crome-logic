SHELL:=/usr/bin/env bash

.PHONY: lint
lint:
	poetry run doc8 -q docs
	poetry run black crome_logic examples
	poetry run pyupgrade
	poetry run pycln crome_logic --all
	poetry run autoflake .
	poetry run isort .
	poetry run autopep8 --in-place -r crome_logic examples
	poetry run docformatter --in-place -r crome_logic examples
	poetry run yapf -ir .

.PHONY: pre-commit
pre-commit:
	pre-commit run --all-files

.PHONY: flake
flake:
	poetry run flake8 crome_logic

.PHONY: mypy
mypy:
	poetry run mypy .

.PHONY: unit
unit:
	poetry run pytest

.PHONY: package
package:
	poetry check
	poetry run pip check
	poetry run safety check --full-report

.PHONY: test
test: lint package unit
