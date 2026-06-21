#!/usr/bin/env bash
set -euo pipefail

# podcast-transcribe/scripts/resolve.sh
# Resolve a podcast URL from any platform to an RSS feed or direct audio URL

URL="${1:-}"
if [[ -z "$URL" ]]; then
    echo "Usage: $0 <podcast-url>" >&2
    exit 1
fi

# Check if whisper is available
if ! command -v whisper &>/dev/null; then
    echo "ERROR: whisper not found. Install via: brew install openai-whisper" >&2
    exit 1
fi

# Check if jq is available
if ! command -v jq &>/dev/null; then
    echo "ERROR: jq not found. Install via: brew install jq" >&2
    exit 1
fi

# ListenNotes API key (free tier: 10,000 requests/month)
# Set LISTENNOTES_API_KEY in your environment or ~/.podcast-transcribe/config
LISTENNOTES_API_KEY="${LISTENNOTES_API_KEY:-}"
if [[ -z "$LISTENNOTES_API_KEY" && -f ~/.podcast-transcribe/config ]]; then
    LISTENNOTES_API_KEY=$(grep -o 'LISTENNOTES_API_KEY=.*' ~/.podcast-transcribe/config | cut -d= -f2- | tr -d '"')
fi

# Detect platform and extract identifiers
PLATFORM="unknown"
IDENTIFIER=""

if [[ "$URL" == *"spotify.com"* || "$URL" == *"open.spotify.com"* ]]; then
    PLATFORM="spotify"
    # Extract show or episode ID
    if [[ "$URL" =~ /episode/([a-zA-Z0-9]+) ]]; then
        IDENTIFIER="${BASH_REMATCH[1]}"
        TYPE="episode"
    elif [[ "$URL" =~ /show/([a-zA-Z0-9]+) ]]; then
        IDENTIFIER="${BASH_REMATCH[1]}"
        TYPE="show"
    fi
elif [[ "$URL" == *"podcasts.apple.com"* || "$URL" == *"itunes.apple.com"* ]]; then
    PLATFORM="apple"
    # Extract podcast ID
    if [[ "$URL" =~ /id([0-9]+) ]]; then
        IDENTIFIER="${BASH_REMATCH[1]}"
        TYPE="podcast"
    fi
elif [[ "$URL" == *"youtube.com"* || "$URL" == *"youtu.be"* ]]; then
    PLATFORM="youtube"
    TYPE="video"
elif [[ "$URL" == *.xml || "$URL" == *"rss"* || "$URL" == *"feed"* ]]; then
    PLATFORM="rss"
    TYPE="rss"
fi

if [[ "$PLATFORM" == "unknown" ]]; then
    echo "ERROR: Unsupported URL platform. Supported: Spotify, Apple Podcasts, YouTube, RSS feeds" >&2
    exit 1
fi

echo "Platform: $PLATFORM"
echo "Type: $TYPE"

# Function to find RSS via ListenNotes
find_rss_listennotes() {
    local query="$1"
    if [[ -z "$LISTENNOTES_API_KEY" ]]; then
        echo "WARNING: No LISTENNOTES_API_KEY set. Cannot search for RSS feed." >&2
        return 1
    fi
    
    local response
    response=$(curl -s "https://listen-api.listennotes.com/api/v2/search?q=${query}&type=podcast" \
        -H "X-ListenAPI-Key: $LISTENNOTES_API_KEY" 2>/dev/null)
    
    if [[ -z "$response" || "$response" == *"error"* ]]; then
        return 1
    fi
    
    # Extract RSS feed from first result
    local rss
    rss=$(echo "$response" | jq -r '.results[0].rss // empty')
    if [[ -n "$rss" && "$rss" != "null" ]]; then
        echo "$rss"
        return 0
    fi
    return 1
}

# Function to get podcast metadata from Spotify (no auth needed for basic info via oEmbed)
get_spotify_metadata() {
    local id="$1"
    local type="$2"
    
    # Try oEmbed endpoint (public, no auth)
    local response
    response=$(curl -s "https://open.spotify.com/oembed?url=https://open.spotify.com/${type}/${id}" 2>/dev/null)
    
    if [[ -n "$response" && "$response" != *"error"* ]]; then
        echo "$response" | jq -r '.title // empty'
    fi
}

# Function to get Apple Podcasts metadata
get_apple_metadata() {
    local id="$1"
    local response
    response=$(curl -s "https://itunes.apple.com/lookup?id=${id}&entity=podcast" 2>/dev/null)
    
    if [[ -n "$response" && "$response" != *"error"* ]]; then
        echo "$response" | jq -r '.results[0].trackName // empty'
    fi
}

# Main resolution logic
RSS_URL=""
TITLE=""

if [[ "$PLATFORM" == "spotify" ]]; then
    # Get metadata from Spotify
    TITLE=$(get_spotify_metadata "$IDENTIFIER" "$TYPE")
    
    if [[ -n "$TITLE" ]]; then
        echo "Title: $TITLE"
        # Search ListenNotes for the RSS feed
        RSS_URL=$(find_rss_listennotes "$TITLE")
    fi
    
    # If that fails, try searching by the Spotify ID through other means
    if [[ -z "$RSS_URL" ]]; then
        # Fallback: Try to construct a search query from the URL
        search_query=$(curl -s "https://open.spotify.com/oembed?url=${URL}" 2>/dev/null | jq -r '.title + " " + .author_name // empty')
        if [[ -n "$search_query" && "$search_query" != " " ]]; then
            RSS_URL=$(find_rss_listennotes "$search_query")
        fi
    fi
    
    if [[ -z "$RSS_URL" ]]; then
        echo "ERROR: Could not find RSS feed for this Spotify podcast." >&2
        echo "The podcast may be Spotify-exclusive (no external RSS feed)." >&2
        exit 1
    fi

elif [[ "$PLATFORM" == "apple" ]]; then
    TITLE=$(get_apple_metadata "$IDENTIFIER")
    if [[ -n "$TITLE" ]]; then
        echo "Title: $TITLE"
        RSS_URL=$(find_rss_listennotes "$TITLE")
    fi
    
    # Fallback: Get RSS directly from iTunes lookup
    if [[ -z "$RSS_URL" ]]; then
        response=$(curl -s "https://itunes.apple.com/lookup?id=${IDENTIFIER}&entity=podcast" 2>/dev/null)
        RSS_URL=$(echo "$response" | jq -r '.results[0].feedUrl // empty')
    fi
    
    if [[ -z "$RSS_URL" ]]; then
        echo "ERROR: Could not find RSS feed for this Apple Podcast" >&2
        exit 1
    fi

elif [[ "$PLATFORM" == "youtube" ]]; then
    # For YouTube, we don't use RSS - we use yt-dlp directly
    echo "Platform: youtube"
    echo "URL: $URL"
    echo "Note: Use youtube-extract skill or yt-dlp for YouTube content"
    exit 0

elif [[ "$PLATFORM" == "rss" ]]; then
    RSS_URL="$URL"
fi

if [[ -n "$RSS_URL" ]]; then
    echo "RSS_URL: $RSS_URL"
    exit 0
else
    echo "ERROR: Could not resolve RSS feed" >&2
    exit 1
fi
