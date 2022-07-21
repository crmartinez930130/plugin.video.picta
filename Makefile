all: lint typecheck test build

.PHONY: build
build: 
	python devscripts/build.py

.PHONY: test
test: 
	python -m pytest tests/

.PHONY: lint
lint: 
	black --check .

.PHONY: typecheck
typecheck:
	mypy --install-types --non-interactive resources/plugin.py
