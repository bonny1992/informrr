FROM lsiobase/alpine:3.11

RUN echo "**** install dependencies ****" && \
    apk add --no-cache python3 && \
    \
    echo "**** install pip ****" && \
    pip3 install --no-cache --upgrade pip setuptools wheel
    
COPY app/ /app

RUN pip install -r /app/requirements.txt


COPY root/ /
VOLUME /data
EXPOSE 5445