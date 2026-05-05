FROM python:3.14.4-alpine

ARG TARGETARCH

COPY install-speedtest.sh .
RUN apk update \
    && apk add --no-cache iperf3 wget \
    && addgroup -S app \
    && adduser -S rover -G app \
    && ./install-speedtest.sh ${TARGETARCH} \
    && chown rover /speedtest

USER rover

COPY --chown=rover:app ./app /app
WORKDIR /app

RUN pip install -r requirements.txt

ENV SPEEDTEST_CMD=/speedtest

ENTRYPOINT [ "python", "main.py" ]