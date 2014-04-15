#!/bin/bash
PID=$(pgrep monitorScale.py)

if [[ -z "$PID" ]]; then
  /usr/local/CoffeeScale/monitorScale.py 2>&1 &
fi
unset PID

PID=$(pgrep reportRead)

if [[ -z "$PID" ]]; then
  /usr/local/CoffeeScale/reportReading.py 2>&1 &
fi
unset PID

