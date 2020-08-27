FROM alpine:3.12

ADD https://github.com/just-containers/s6-overlay/releases/download/v2.0.0.1/s6-overlay-amd64.tar.gz /tmp/
RUN gunzip -c /tmp/s6-overlay-amd64.tar.gz | tar -xf - -C /

RUN echo "**** install dependencies ****" && \
    apk add --no-cache python3 bash && \
    \
    echo "**** install pip ****" && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi
    
ENV LIBRARY_PATH=/lib:/usr/lib

COPY root/ /

COPY app/ /app

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

VOLUME /data

EXPOSE 5445

ENTRYPOINT ["/init"]