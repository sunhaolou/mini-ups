#!/bin/bash
# This will restart the server if it crashes
while true; do
    python3 manage.py runserver 0.0.0.0:8000
    echo "Server crashed, restarting..."
    sleep 1
done
