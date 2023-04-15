FROM ubuntu:latest
WORKDIR /root/
COPY . .
USER root
RUN apt-get update && apt-get install tcpdump inotify-tools util-linux curl -y
CMD ["./honeypot", "start"]
