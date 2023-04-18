#!/bin/bash
set -e
HONEYPOT_PATH=${HONEYPOT_PATH:-$1}
MONITORING_PATH=${MONITORING_PATH:-$2}

if [[ -z "${HONEYPOT_PATH}" || -z  "${MONITORING_PATH}" ]]; then
    echo "Please set: HONEYPOT_PATH and MONITORING_PATH environment variables!">&2
    exit 1
fi

COMPOSE_CMD="docker-compose"
if ! command -v docker-compose &> /dev/null
then
  COMPOSE_CMD="docker compose"
fi

# Start honeypot in custom network
$COMPOSE_CMD -f $HONEYPOT_PATH pull

$COMPOSE_CMD -f $HONEYPOT_PATH up -d
honeypot_container_id=$($COMPOSE_CMD -f $HONEYPOT_PATH ps -q)
echo $honeypot_container_id > $(dirname $HONEYPOT_PATH)/honeypot_id
# Get honeypot brdige name to filter the communication from bridge interface
honeypot_network=$(docker container inspect --format '{{range $net,$v := .NetworkSettings.Networks}}{{printf "%s\n" $net}}{{end}}' $honeypot_container_id)
network_id=$(docker network inspect -f {{.Id}} $honeypot_network)
bridge_name="br-${network_id:0:12}"

# Set bridge to monitoring EXTRA_ARGS so tcpdump monitores the created brdige
export EXTRA_ARGS="-i $bridge_name"

# Get honeypot IP which will be used to filter the honeypot communication
export HONEYPOT_ADDR=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $honeypot_container_id)

# Start monitoring
$COMPOSE_CMD -f $MONITORING_PATH up -d
echo $($COMPOSE_CMD -f $MONITORING_PATH ps -q) > $(dirname $HONEYPOT_PATH)/monitoring_id
