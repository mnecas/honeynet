FROM ubuntu:latest
WORKDIR /code/
COPY . .
RUN apt-get update -y && apt-get install tcpdump inotify-tools util-linux curl libcap2-bin -y
RUN groupadd -r tcpdumpuser && useradd -r -g tcpdumpuser tcpdumpuser
RUN groupadd pcap
RUN usermod -a -G pcap tcpdumpuser
RUN chgrp pcap /usr/bin/tcpdump
RUN chmod 750 /usr/bin/tcpdump
RUN setcap cap_net_raw,cap_net_admin=eip /usr/bin/tcpdump
USER tcpdumpuser
CMD ["./honeypot", "start"]
