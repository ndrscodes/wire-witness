#!/bin/sh

TARGETARCH=$1

if [ -z "$TARGETARCH" ]; then
    TARGETARCH="x86_64"
elif [ "$TARGETARCH" = "arm64" ]; then
    TARGETARCH="aarch64"
elif [ "$TARGETARCH" = "amd64" ]; then
    TARGETARCH="x86_64"
fi
URL="https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-linux-$TARGETARCH.tgz"

wget $URL -O speedtest.tgz 

tar -xzf speedtest.tgz
chmod +x speedtest
rm speedtest.tgz