#!/bin/sh
pylint --rcfile=pylint.rc --fail-under=9 $(git ls-files 'src/saftig/*.py')
