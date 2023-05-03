#!/bin/sh -e
set -x

# Sort imports one per line, so autoflake can remove unused imports
isort --force-single-line-imports --apply backend/app
sh ./backend/app/scripts/format.sh
