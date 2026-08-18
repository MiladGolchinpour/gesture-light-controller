#!/bin/bash

PORT=${1:-$(ls /dev/cu.usbserial* /dev/cu.wchusb* 2>/dev/null | head -n 1)}

if [ -z "$PORT" ]; then
    echo "Wemos not found"
    exit 1
fi

echo "Using port: $PORT"

mpremote connect $PORT reset

mpremote cp wemos/config.py :
mpremote cp wemos/tm1637.py :

sleep 1

mpremote connect $PORT run wemos/main.py