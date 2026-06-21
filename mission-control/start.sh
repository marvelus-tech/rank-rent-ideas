#!/bin/bash
# Start Mission Control Server
# This serves the dashboard and handles refresh requests

cd "$(dirname "$0")"
/usr/local/Cellar/node@22/22.22.1_3/bin/node server.js
