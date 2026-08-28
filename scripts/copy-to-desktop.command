#!/bin/bash
# Double-click on a Mac to put the 1,300 Bibles in folders on the Desktop.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/copy_holy_bibles_to_desktop.py
open "$HOME/Desktop/Christ Supply Holy Bible"
