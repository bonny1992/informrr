FROM --platform=$BUILDPLATFORM lsiobase/alpine:3.11

LABEL org.opencontainers.image.source https://github.com/bonny1992/informrr

RUN echo "**** install dependencies ****" && \
    apk add --no-cache python3 && \
    \
    echo "**** install pip ****" && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi
    
COPY app/ /app

RUN pip install -r /app/requirements.txt


COPY root/ /
VOLUME /data
EXPOSE 5445