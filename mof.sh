#! /usr/bin/env bash

set -eo pipefail

readonly PROGDIR=$(dirname $0)
readonly ARGS="$@"

${PROGDIR}/mof/mof.py $ARGS
