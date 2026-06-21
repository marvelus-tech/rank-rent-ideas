#!/bin/bash
# Cody Trigger Script
# Auto-detects presentation/web requests and routes to Cody agent

KEYWORDS="presentation|deck|website|landing page|webpage|site|showcase|portfolio|dashboard|marketing site|web app|frontend|UI|design|page|component"

if echo "$1" | grep -qiE "$KEYWORDS"; then
    echo "🎨 Routing to Cody — Elite Design Agent"
    echo "Loading design skills..."
    
    # Read Cody's configuration
    cat ~/.openclaw/workspace/CODY.md
    
    # Spawn Cody with context
    echo "Spawning Cody agent..."
    exit 0
else
    echo "No design keywords detected"
    exit 1
fi
