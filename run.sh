#!/usr/bin/env bash
set -e
mkdir -p output
python -m stress.run
python -m unittest discover -s tests -t .
