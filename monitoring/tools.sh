#!/bin/bash

RED="\e[31m"
GREEN="\e[32m"
YELLOW="\e[33m"
BLUE="\e[34m"
ENDCOLOR="\e[0m"

DEBUG=${DEBUG:0}
HONEYPOT_SERVER=${SERVER:-"127.0.0.1:8000"}

err() {
    echo -e "$RED[$(date +'%Y-%m-%dT%H:%M:%S%z')][ERROR]: $*$ENDCOLOR" >&2
}

debug() {
    if [[ $DEBUG -gt 0 ]]
    then
        echo -e "$BLUE[$(date +'%Y-%m-%dT%H:%M:%S%z')][DEBUG]: $*$ENDCOLOR" >&1
    fi
}

send(){
    endpoint="$1"
    data_params="${@: 2}"
    debug "Endpoint: $endpoint"
    debug "Data params: $data_params"

    curl \
        -H "Authorization: Token $TOKEN" \
        --fail \
        --connect-timeout 5 \
        --max-time 10 \
        --retry 10 \
        --retry-delay 0 \
        --retry-max-time 40 \
        --retry-all-errors \
        $data_params \
        http://$HONEYPOT_SERVER/api/$ID/$endpoint
}
