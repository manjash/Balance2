#!/usr/bin/env bash

set -x

mypy app
black app --check
isort --recursive --check-only backend/app/app
flake8 --max-line-length=120 --extend-exclude=venv/ --select=C,E,F,W,B,B950 --ignore=E302,E305,E203,E501,W503 backend/app/app/
