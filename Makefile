all: test build

.PHONY: build
build: 
	python devscripts/build.py

.PHONY: test
test: 
	python -m unittest discover -v

.PHONY: typecheck
typecheck:
	mypy --install-types --non-interactive resources/plugin.py
