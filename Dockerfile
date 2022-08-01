FROM lsiobase/alpine:3.12

RUN echo "**** install dependencies ****" && \
    apk add --no-cache python3 py3-pip && \
    mv /usr/bin/lsb_release /usr/bin/lsb_release_back && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi
COPY app/ /app

RUN pip3 install -r /app/requirements.txt


COPY root/ /
VOLUME /data
EXPOSE 5445


# FROM lsiobase/alpine:3.11

# RUN echo "**** install dependencies ****" && \
#     apk add --no-cache python3 && \
#     \
#     echo "**** install pip ****" && \
#     python3 -m ensurepip && \
#     rm -r /usr/lib/python*/ensurepip && \
#     pip3 install --no-cache --upgrade pip setuptools wheel && \
#     if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
#     if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi
    
# COPY app/ /app

# RUN pip install -r /app/requirements.txt


# COPY root/ /
# VOLUME /data
# EXPOSE 5445