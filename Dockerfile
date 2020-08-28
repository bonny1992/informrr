FROM lsiobase/alpine:3.11

RUN echo "**** install dependencies ****" && \
    apk add --no-cache python3 && \
    \
    echo "**** install pip ****" && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    rm -r /root/.cache
    
COPY app/ /app

RUN pip install -r /app/requirements.txt


COPY root/ /
VOLUME /data
EXPOSE 5445