#!/usr/bin/env sh
if [ ! -d sphinx_pyreverse ]; then
	printf "This script needs to be run from the directory that contains the sphinx_pyreverse module\\n"
	exit 3
fi

NOSE2_EXE=$(command -v nose2)
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
	printf "Tests: Failed to find nose2\\n"
	exit $EXIT_CODE
fi
if [ -z "$NOSE2_EXE" ]; then
	printf "Tests: Failed to find nose2\\n"
	exit 2
fi

# Runs the unit-tests and the code coverage at the same-time
python -m coverage run --rcfile=.coveragerc "$NOSE2_EXE" --config unitest.cfg --fail-fast
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
	exit $EXIT_CODE
fi

# Generates the HTML code-coverage report
coverage html --rcfile=.coveragerc
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
	exit $EXIT_CODE
fi

# Get the coverage percentage
COVERAGE=$(coverage report --rcfile=.coveragerc -m --omit=*python*-packages* | grep "TOTAL.\+" | awk '{print $6}')
if [ "$COVERAGE" != "100%" ]; then
	# if we only have a single file we need to look at that file only
	COVERAGE=$(coverage report --rcfile=.coveragerc -m --omit=*python*-packages* | grep "%" | awk '{print $6}')
	if [ "$COVERAGE" != "100%" ]; then
		printf "COVERAGE: Failed: '%s' is not '100%%' \\n" "$COVERAGE"
		exit 2
	fi
fi

# Checks the syntax of all the files match the standards
find . -iname "*.py" -not -ipath "./*env/*" -print0 | xargs -0 python -m flake8
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
	printf "FLAKE8: Failed\\n"
	exit $EXIT_CODE
fi

# Checks the syntax of all the files match the standards
find sphinx_pyreverse -iname "*.py" -not -ipath "./*env/*" -print0 | xargs -0 python -m pylint -E
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
	printf "pylint: Failed\\n"
	exit $EXIT_CODE
fi
