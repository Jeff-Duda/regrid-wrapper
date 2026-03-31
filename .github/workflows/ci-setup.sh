#!/usr/bin/env bash

set -eu

. $GITHUB_WORKSPACE/.github/workflows/ci-env.sh

pip install -e .
