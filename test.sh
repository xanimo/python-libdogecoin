#!/bin/bash
export LC_ALL=C
set -e -o pipefail

TARGET_WHEEL=$(find . -maxdepth 2 -type f -regex ".*libdogecoin-.*")
python -m pip install --upgrade wheel pytest
wheel unpack "$TARGET_WHEEL"
cp -r libdogecoin-*/* .
python -m pytest
rm -rf *.so *.pyd libdogecoin-*/ *.libs tests/__pycache__ .pytest_cache
