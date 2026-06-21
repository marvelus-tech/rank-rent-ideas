#!/bin/bash
# Enable GitHub Pages for all dashboards

TOKEN=$(gh auth status -t 2>/dev/null | grep -o 'gho_[a-zA-Z0-9]*' || echo "")

REPOS=(
  "marvelus-tech/tko-intel-feed"
  "marvelus-tech/rank-rent-niches"
  "marvelus-tech/solana-alpha"
  "marvelus-tech/marvelus-leads"
  "marvelus-tech/brownstone-audio"
)

for REPO in "${REPOS[@]}"; do
  echo "Enabling Pages for $REPO..."
  curl -X POST \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "https://api.github.com/repos/${REPO}/pages" \
    -d '{"source":{"branch":"main","path":"/"}}' 2>/dev/null
  echo ""
done

echo "All Pages enabled!"