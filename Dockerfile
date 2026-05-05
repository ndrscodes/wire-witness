FROM python:3.14.4-alpine

RUN apk update \
    && apk add --no-cache iperf3 wget \
    && addgroup -S app \
    && adduser -S rover -G app 
USER rover

COPY --chown=rover:app ./app /app
WORKDIR /app

RUN wget https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-linux-x86_64.tgz -O speedtest.tgz \
    && tar -xzf speedtest.tgz \
    && pip install -r requirements.txt

ENV SPEEDTEST_CMD=/app/speedtest

ENTRYPOINT [ "python", "main.py" ]