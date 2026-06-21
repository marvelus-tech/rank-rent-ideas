#!/bin/bash
export PATH="/usr/local/Cellar/node@22/22.22.1_3/bin:/usr/local/bin:$PATH"
export HOME="/Users/oktos"
cd "/Users/oktos/.openclaw/workspace/skills/presence-detection"
mkdir -p /tmp/openclaw
exec /usr/local/Cellar/node@22/22.22.1_3/bin/node presence-listener.js >> /tmp/openclaw/presence-listener.log 2>&1
