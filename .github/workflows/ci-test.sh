#!/usr/bin/env bash

set -eu

. $GITHUB_WORKSPACE/.github/workflows/ci-env.sh

echo "running serial tests..."
pytest -v src

echo "running parallel tests..."
mpirun --allow-run-as-root --oversubscribe -n 8 pytest -v -m "mpi and not integration" src/test
