#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place backend/app --exclude=__init__.py
black backend/app
isort --apply backend/app
