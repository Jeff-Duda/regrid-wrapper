#!/usr/bin/env bash

set -eux

docker push deckyfre/regrid-wrapper-spack:0.0.5
docker push deckyfre/regrid-wrapper-spack:latest

docker push deckyfre/regrid-wrapper-ci:0.0.3
docker push deckyfre/regrid-wrapper-ci:latest
