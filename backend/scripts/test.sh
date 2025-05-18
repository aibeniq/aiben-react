#!/usr/bin/env bash
set -e
set -x

# Use the Python interpreter from the virtual environment
coverage run --source=app -m pytest
coverage report --show-missing
coverage html --title "${@-coverage}"