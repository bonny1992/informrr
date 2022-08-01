FROM lsiobase/alpine:3.11

RUN echo "**** install dependencies ****" && \
    apk add --no-cache python3 python3-pip
    
COPY app/ /app

RUN pip install -r /app/requirements.txt


COPY root/ /
VOLUME /data
EXPOSE 5445