#!/usr/bin/env python3
"""
R&D Analyst Watcher
Monitors analyst-queue/ and spawns Analyst sub-agent when new intel arrives.
Run this as a background process or via launchd keep-alive.
"""

import os
import time
import json
import subprocess
from datetime import datetime, timezone

RND_DIR = "/Users/oktos/.openclaw/workspace/.rnd"
QUEUE_DIR = f"{RND_DIR}/analyst-queue"
PROCESSING_DIR = f"{RND_DIR}/analyst-processing"
COMPLETED_DIR = f"{RND_DIR}/opportunities"
LOG_FILE = f"{RND_DIR}/logs/analyst-watcher.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def process_intel(intel_file):
    """Spawn Analyst sub-agent to process this intel file"""
    filename = os.path.basename(intel_file)
    processing_file = f"{PROCESSING_DIR}/{filename}"
    
    # Move to processing
    os.rename(intel_file, processing_file)
    log(f"Processing: {filename}")
    
    # Read intel
    with open(processing_file, "r") as f:
        intel = json.load(f)
    
    episode_title = intel.get("title", "Unknown")
    
    # Create task for Analyst
    task_file = f"{RND_DIR}/tasks/analyst-{filename}"
    os.makedirs(os.path.dirname(task_file), exist_ok=True)
    
    task = {
        "type": "tko-analysis",
        "episode_title": episode_title,
        "intel_file": processing_file,
        "output_dir": COMPLETED_DIR,
        "priority": "P1",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    with open(task_file, "w") as f:
        json.dump(task, f, indent=2)
    
    log(f"Task created: {task_file}")
    
    # Signal to main agent (Penelopi) that Analyst work is ready
    # This creates a notification that the user can see
    notification = f"""
🎯 R&D ANALYST TASK READY

Episode: {episode_title}
Status: Waiting for analysis
Action: Spawn Analyst sub-agent to generate Opportunity Card

Task file: {task_file}
"""
    
    # Write to a signal file that can be checked
    signal_file = f"{RND_DIR}/.analyst-ready"
    with open(signal_file, "w") as f:
        f.write(notification)
    
    log("Analyst task ready for spawning")
    return task_file

def main():
    log("=" * 50)
    log("R&D Analyst Watcher starting...")
    
    os.makedirs(QUEUE_DIR, exist_ok=True)
    os.makedirs(PROCESSING_DIR, exist_ok=True)
    os.makedirs(COMPLETED_DIR, exist_ok=True)
    
    # Process any existing queued files
    queued_files = [f for f in os.listdir(QUEUE_DIR) if f.endswith(".json")]
    
    for filename in queued_files:
        intel_file = f"{QUEUE_DIR}/{filename}"
        log(f"Found queued: {filename}")
        process_intel(intel_file)
    
    if not queued_files:
        log("No queued intel files. Scout will add them when new episodes drop.")
    
    log("Watcher ready. Monitoring for new intel...")
    
    # Keep running and check every 60 seconds
    while True:
        time.sleep(60)
        
        queued_files = [f for f in os.listdir(QUEUE_DIR) if f.endswith(".json")]
        
        for filename in queued_files:
            intel_file = f"{QUEUE_DIR}/{filename}"
            log(f"New intel detected: {filename}")
            process_intel(intel_file)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Watcher stopped.")
