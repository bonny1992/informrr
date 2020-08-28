FROM lsiobase/alpine:3.11

COPY app/ /app

RUN pip install -r /app/requirements.txt


COPY root/ /
VOLUME /data
EXPOSE 5445