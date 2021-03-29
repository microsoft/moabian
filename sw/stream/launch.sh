#!/usr/bin/env bash
/home/pi/.local/bin/gunicorn stream:app \
    --workers 2 \
    --bind unix:/tmp/web.sock \
    --timeout 120 \
    --log-level=info \
    --capture-output \
    --error-logfile='/tmp/gunicorn.error.log' \
    --access-logfile='/tmp/gunicorn.access.log' \
