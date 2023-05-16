#!/bin/bash
set -e

SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
python3 $SCRIPT_DIR/../manage.py send_logs --honeynet $1
