#!/usr/bin/env bash
set -o pipefail
set -e

while getopts u:p:rh option
do
case "${option}"
in
r) DO_RELEASE=1;;
h) printf " [-u <username>] [-p <password>] [-r ]\n"
   printf "  -r: Releases to the master repository\n"
   printf "  uses the .pypirc config"
   ;;
*) exit 3;; # unknown options
esac
done

if [ ! -d sphinx_pyreverse ]; then
	printf "sphinx_pyreverse: Please rerun in the sphinx_pyreverse module's parent dir\\n"
	exit 3
fi

if [ -z "$DO_RELEASE" ]; then
	# Default to uploading to pip testing first
	# IMPORTANT: You can only load a file tagged for a project, for a build once
	PIP_REPOSITORY=https://test.pypi.org/legacy/
else
	if [ -z "$SPHINX_PYREVERSE_FORCE_RELEASE" ]; then
		# We're not in a CI/CD build, as SPHINX_PYREVERSE_FORCE_RELEASE is not set
		printf "This will release the build to the main pip repository and cannot be undone.\\n"
		printf "Think carefuly before continuing\\n"
		read -p "  Are you sure you want to release this version? [yN] " -r choice
		case "$choice" in
			y|Y ) echo "sphinx_pyreverse: releasing...";;
			n|N ) exit 5;;
			* ) exit 3;;
		esac
	fi
	PIP_REPOSITORY="" #https://pypi.python.org/pypi
fi

if [ -d dist ]; then
	# Back up to a separate directory to avoid the upload tools globbing already
	# uploaded files
	BACKUP_DIR="dist_backups/$(date +"%Y-%m-%d_%H-%M-%S")"
	mkdir -p "$BACKUP_DIR"
	mv dist/* "$BACKUP_DIR"
fi

python3 setup.py sdist bdist_wheel | sed 's/^/py3: /'

python3 -m twine upload --verbose --repository sphinx-pyreverse dist/* | sed 's/^/upload: /'
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
	printf "sphinx_pyreverse: Failed to upload dist/*, files may already have been uploaded\\n"
	printf "sphinx_pyreverse:    Try updating the version in setup.py and trying again.\\n"
	exit 4
fi
