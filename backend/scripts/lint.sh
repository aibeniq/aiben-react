#!/usr/bin/env bash

set -e
set -x

mypy app
ruff check app
black --check app
