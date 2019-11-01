#!/usr/bin/env sh
set -o pipefail

if [ ! -d sphinx_pyreverse ]; then
	printf "This script needs to be run from the directory that contains the sphinx_pyreverse module\\n"
	exit 3
fi

for python_version in "python2" "python3"; do
  VENV_DIR="$python_version"_venv
  if [ ! -d "$VENV_DIR" ]; then
    virtualenv -p "$python_version" "$VENV_DIR"
  fi

  echo "------------------------- $python_version -------------------------"

  source "$VENV_DIR"/bin/activate || exit 2

  pip install -r pip-requirements-test 2>&1 | sed 's/^/'"$python_version"': /' || exit 2

  ./scripts/runners/run_test.sh 2>&1 | sed 's/^/'"$python_version"': /' || exit 2

  deactivate || exit 2
done
