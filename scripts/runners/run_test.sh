#!/usr/bin/env sh
if [ ! -d sphinx_pyreverse ]; then
	printf "This script needs to be run from the directory that contains the sphinx_pyreverse module\\n"
	exit 3
fi

printf "Finding files to test "
printf "with find...\\n"
PYTHON_FILES=$(find "$(pwd)" -iname "*.py" -not -ipath "$(pwd)/*env/*" -not -ipath "$(pwd)/build/*"  -not -ipath "$(pwd)/.rope*/*" -print)
printf "    %s python files found/changed.\\n" "$(echo "$PYTHON_FILES" | wc -l)"

# Runs the unit-tests and the code coverage at the same-time
CMD_PYTEST="python3 -m pytest --cov=. --cov-config="$(pwd)"/.coveragerc --cov-fail-under=100 -c "$(pwd)"/unittest.cfg --failed-first --exitfirst $(pwd)/test/"
printf "%s\\n" "$CMD_PYTEST"
$CMD_PYTEST #2>&1 | sed -e 's/^/PYTEST: /g'
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
	exit $EXIT_CODE
fi

# Checks the syntax of all the files match the standards
python -m flake8 $PYTHON_FILES
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
	printf "FLAKE8: Failed\\n"
	exit $EXIT_CODE
fi

# Checks the syntax of all the files match the standards
python -m pylint --rcfile="$(pwd)"/.pylint.rc $PYTHON_FILES
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
	printf "pylint: Failed\\n"
	exit $EXIT_CODE
fi
