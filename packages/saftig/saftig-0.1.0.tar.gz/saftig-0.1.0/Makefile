SHELL := /bin/bash

all: build doc test linter
ie:
	pip install --no-build-isolation -e .

test:
	coverage run -m unittest discover .
coverage:
	coverage report
cweb:
	coverage html && open htmlcov/index.html

linter:
	./tooling/run_linter.sh
linter_testing:
	./tooling/run_linter_tests.sh
lt: linter_testing

doc: doc/source/* doc/*
	cd doc/ && $(MAKE) html

view: doc
	open doc/build/html/index.html

clean:
	-rm -r build/
	-rm -r dist/
	-rm -r saftig/__pycache__/
	-rm *.so
	-rm saftig/*.so
	-rm -r SAFTIG.egg-info/
	-rm -r htmlcov

testpublish:
	python -m build -s
	twine upload --repository testpypi dist/*

.PHONY: all, doc, view, test, linter, coverage, cweb, linter_testing, lt, build, clean, testpublish, ie
