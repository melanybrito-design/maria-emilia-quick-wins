#!/bin/sh
cd "$(dirname "$0")" || exit 1
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv || exit 1
  .venv/bin/python -m pip install --no-index --find-links wheelhouse -r requirements.txt || exit 1
fi
exec .venv/bin/python main.py --serve
