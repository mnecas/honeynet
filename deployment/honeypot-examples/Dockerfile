
FROM ubuntu:latest
RUN apt update && apt install  openssh-server sudo -y
RUN useradd -rm -d /home/test -s /bin/bash -g root -G sudo -u 1000 test
RUN echo 'test:test' | chpasswd
RUN service ssh start

RUN echo 'PROMPT_COMMAND="echo -n [$(date +%H%M)]"' >> /etc/bash.bashrc
RUN echo "readonly PROMPT_COMMAND" >> /etc/bash.bashrc

EXPOSE 22
CMD ["/usr/sbin/sshd","-D", "-e"]
