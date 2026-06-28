#!/bin/bash
# Craigslist Land Finder - Daily Search Script
# Usage: ./craigslist-landfinder.sh [market] [max_price]

MARKET=${1:-"austin"}
MAX_PRICE=${2:-50000}
QUERY="land"

URL="https://${MARKET}.craigslist.org/search/rea?purveyor=owner&query=${QUERY}&max_price=${MAX_PRICE}&sort=date"

echo "Searching Craigslist for land deals in ${MARKET}..."
echo "URL: ${URL}"

# Open browser for manual review
open "${URL}"

echo "Review listings and copy promising deals to dashboard."
