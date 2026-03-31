#!/usr/bin/env bash

set -eu

. $GITHUB_WORKSPACE/.github/workflows/ci-env.sh

git config --global --add safe.directory $GITHUB_WORKSPACE
pre-commit run --all
