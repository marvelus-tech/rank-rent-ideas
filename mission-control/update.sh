#!/bin/zsh
# Mission Control Daily Update Cron Job
# Updates projects.json from Obsidian Ideas vault

/usr/local/Cellar/node@22/22.22.1_3/bin/node /Users/oktos/.openclaw/workspace/mission-control/scan-ideas.js >> /tmp/mission-control-cron.log 2>&1
