#!/bin/sh
docker events --filter 'event=start' --filter 'event=stop' | while read event

do
  
    container_id=`echo $event | sed 's/.*Z\ \(.*\):\ .*/\1/'`

    echo $container_id

    ipaddress=`docker inspect --format='{{.NetworkSettings.IPAddress}}' $container_id`
    port=`docker inspect --format='{{(index (index .NetworkSettings.Ports "80/tcp") 0).HostPort}}' $container_id`
    domain=`docker inspect --format='{{.Config.Domainname}}' $container_id`
    host=`docker inspect --format='{{.Config.Hostname}}' $container_id`
    
    echo $ipaddress
    echo $port
    echo $host.$domain

done
