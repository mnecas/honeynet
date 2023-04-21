
# /var/lib/docker/containers/<container_id>/<container_id>-json.log

# docker inspect --format="{{.LogPath}}" 250005753d3d

# sudo sh -c 'echo "" > $(docker inspect --format="{{.LogPath}}" 250)'


# log in /var/log/cron
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
# echo "$SCRIPT_DIR" >> /tmp/test
python3 $SCRIPT_DIR/../manage.py send_logs --honeynet $1
