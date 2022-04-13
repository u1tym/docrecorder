FROM ubuntu:18.04
ENV TZ=Asia/Tokyo
ENV USER=recusr
ENV GROUP=recusr
ENV UID=1001
ENV GID=1001
ENV PASS=recusr
ENV RPSS=bdntspa7
RUN echo $TZ > /etc/timezone \
 && apt-get -y update
RUN DEBIAN_FRONTEND=nointeractive apt-get install -y --no-install-recommends \
 rtmpdump \
 libxml2-utils \
 ffmpeg \
 libavcodec-extra \
 curl \
 tzdata \
 gosu \
 ca-certificates
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime
RUN echo root:$RPSS | chpasswd \
 && addgroup --gid $GID $GROUP \
 && adduser -q --gecos GECOS --disabled-login --uid $UID --gid $GID --home /home/$USER $USER \
 && echo $USER:$PASS | chpasswd
COPY files/rec_radiko.sh /home/$USER/.
COPY files/rec_agp.sh /home/$USER/.
COPY files/dot.local.python3.8.tgz /home/$USER/.
COPY files/do_main.bash /home/$USER/.
COPY files/main.py /home/$USER/.
COPY files/log.py /home/$USER/.
RUN mkdir -p /home/$USER/log \
 && mkdir -p /home/$USER/data \
 && chown $USER:$USER /home/$USER/log \
 && chown $USER:$USER /home/$USER/data \
 && chown $USER:$USER /home/$USER/rec_radiko.sh \
 && chown $USER:$USER /home/$USER/rec_agp.sh \
 && chown $USER:$USER /home/$USER/dot.local.python3.8.tgz \
 && chown $USER:$USER /home/$USER/do_main.bash \
 && chown $USER:$USER /home/$USER/main.py \
 && chown $USER:$USER /home/$USER/log.py
USER $USER
RUN cd /home/$USER \
 && echo "export LANG=ja_JP.UTF8" >> .bashrc \
 && tar xzvf dot.local.python3.8.tgz \
 && echo "PATH=/home/${USER}/.local/python/bin:\${PATH}" >> .bashrc \
 && rm -rf dot.local.python3.8.tgz \
 && mkdir -p /home/${USER}/data \
 && chmod +x /home/${USER}/rec_radiko.sh \
 && chmod +x /home/${USER}/rec_agp.sh \
 && chmod +x /home/${USER}/do_main.bash
ENTRYPOINT [ "/home/recusr/do_main.bash" ]

