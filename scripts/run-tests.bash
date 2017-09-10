#!/bin/sh

# created the pre-commit tests following the tutorial on: 
# https://sigmoidal.io/automatic-code-quality-checks-with-git-hooks/

# if any command inside script returns error, exit and return that error 
set -e

# magic line to ensure that we're always inside the root of our application,
# no matter from which directory we'll run script
# thanks to it we can just enter `./scripts/run-tests.bash`
cd "${0%/*}/.."

echo "Running tests"
echo "............................" 

nosetests -v
