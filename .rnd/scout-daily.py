#!/usr/bin/env python3
"""
R&D Scout - Daily TKO Content Monitor
Polls RSS feed for new episodes, extracts metadata, triggers Analyst if new content found.
"""

import urllib.request
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime, timezone

RND_DIR = "/Users/oktos/.openclaw/workspace/.rnd"
RSS_URL = "https://feeds.buzzsprout.com/2241079.rss"
STATE_FILE = f"{RND_DIR}/state/last-check.json"
INTEL_RAW_DIR = f"{RND_DIR}/intel/raw"
LOG_FILE = f"{RND_DIR}/logs/scout.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_episode_title": None, "last_check": None}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def fetch_rss():
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(RSS_URL, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()

def parse_episodes(xml_data):
    root = ET.fromstring(xml_data)
    items = root.findall(".//item")
    episodes = []
    for item in items[:5]:  # Check 5 most recent
        title = item.find("title").text if item.find("title") is not None else "No title"
        pub_date = item.find("pubDate").text if item.find("pubDate") is not None else None
        description = item.find("description")
        desc_text = description.text if description is not None else ""
        link = item.find("link")
        url = link.text if link is not None else ""
        
        enclosure = item.find("enclosure")
        audio_url = enclosure.get("url") if enclosure is not None else None
        
        episodes.append({
            "title": title,
            "pub_date": pub_date,
            "description": desc_text[:500],  # First 500 chars
            "url": url,
            "audio_url": audio_url,
            "found_at": datetime.now(timezone.utc).isoformat()
        })
    return episodes

def save_raw_intel(episode):
    os.makedirs(INTEL_RAW_DIR, exist_ok=True)
    safe_title = episode["title"].replace(" ", "_").replace("/", "_")[:50]
    filename = f"{INTEL_RAW_DIR}/{datetime.now().strftime('%Y%m%d')}_{safe_title}.json"
    with open(filename, "w") as f:
        json.dump(episode, f, indent=2)
    return filename

def trigger_analyst(intel_file):
    """Signal that Analyst should process this file"""
    trigger_file = f"{RND_DIR}/analyst-queue/{os.path.basename(intel_file)}"
    os.makedirs(os.path.dirname(trigger_file), exist_ok=True)
    
    with open(intel_file, "r") as f:
        data = json.load(f)
    
    data["queued_for_analysis"] = datetime.now(timezone.utc).isoformat()
    
    with open(trigger_file, "w") as f:
        json.dump(data, f, indent=2)
    
    log(f"Queued for Analyst: {trigger_file}")
    return trigger_file

def main():
    log("=" * 50)
    log("R&D Scout waking up...")
    
    state = load_state()
    log(f"Last check: {state.get('last_check', 'Never')}")
    log(f"Last episode: {state.get('last_episode_title', 'None')}")
    
    try:
        xml_data = fetch_rss()
        episodes = parse_episodes(xml_data)
        
        if not episodes:
            log("No episodes found in RSS")
            save_state({**state, "last_check": datetime.now(timezone.utc).isoformat()})
            return
        
        latest = episodes[0]
        log(f"Latest episode: {latest['title']}")
        
        # Check if this is new
        if latest["title"] == state.get("last_episode_title"):
            log("No new episodes since last check")
            save_state({**state, "last_check": datetime.now(timezone.utc).isoformat()})
            return
        
        # New episode found!
        log(f"🎯 NEW EPISODE DETECTED: {latest['title']}")
        
        # Save raw intel
        intel_file = save_raw_intel(latest)
        log(f"Saved raw intel: {intel_file}")
        
        # Queue for Analyst
        trigger_file = trigger_analyst(intel_file)
        
        # Update state
        save_state({
            "last_episode_title": latest["title"],
            "last_check": datetime.now(timezone.utc).isoformat(),
            "last_intel_file": intel_file
        })
        
        log("Scout complete. Analyst will process.")
        
    except Exception as e:
        log(f"ERROR: {str(e)}")
        raise

if __name__ == "__main__":
    main()
