#!/bin/bash
export LC_ALL=C
set -e -o pipefail

p=python3
TARGET_WHEEL=$(find . -maxdepth 2 -type f -regex ".*libdogecoin-.*")
$p -m venv .venv
source .venv/bin/activate
$p -m pip install --upgrade wheel pytest
wheel unpack "$TARGET_WHEEL"
cp -r libdogecoin-*/* .
$p -m pytest
deactivate
rm -rf .venv *.so libdogecoin-*/ *.libs tests/__pycache__ .pytest_cache
