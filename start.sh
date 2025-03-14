#!/bin/bash
nginx
ffmpeg -re -i "https://uselector.cdn.intigral-ott.net/MB2H/MB2H.isml/manifest.mpd" \
       -decryption_key 58fa20cf6055f3aefc15707992c0b685 \
       -c:v copy -c:a copy -f flv rtmp://localhost/live/stream
