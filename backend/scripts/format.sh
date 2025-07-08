#!/bin/sh -e
set -x

ruff check app scripts --fix
black app scripts
