#!/bin/bash
set -e

HONEYPOT_PATH=${HONEYPOT_PATH:-$1}
MONITORING_PATH=${MONITORING_PATH:-$2}
if [[ -z "${MONITORING_PATH}" || -z  "${HONEYPOT_PATH}" ]]; then
    echo "Please set: MONITORING_PATH and HONEYPOT_PATH environment variables!"
    exit 1
fi

COMPOSE_CMD="docker-compose"
if ! command -v docker-compose &> /dev/null
then
  COMPOSE_CMD="docker compose"
fi

# Stop honeypot
$COMPOSE_CMD -f $HONEYPOT_PATH down

# Stop monitoring
$COMPOSE_CMD -f $MONITORING_PATH down

# Remove stopped honeypot
$COMPOSE_CMD -f $HONEYPOT_PATH rm -f

# Remove stopped  monitoring
$COMPOSE_CMD -f $MONITORING_PATH rm -f
