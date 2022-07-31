FROM lsiobase/alpine:3.11

RUN echo "**** install dependencies ****" && \
    apk add --no-cache python3 py3-setuptools py3-wheel
    
COPY app/ /app

RUN pip install -r /app/requirements.txt


COPY root/ /
VOLUME /data
EXPOSE 5445