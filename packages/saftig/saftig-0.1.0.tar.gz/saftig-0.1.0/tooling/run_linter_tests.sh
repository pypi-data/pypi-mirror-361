#!/bin/sh
pylint --rcfile=tooling/pylint_testing.rc --fail-under=9 $(git ls-files 'src/testing/*.py')
