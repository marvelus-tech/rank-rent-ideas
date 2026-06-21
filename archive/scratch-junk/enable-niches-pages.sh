#!/bin/bash
# Enable GitHub Pages via API

REPO="marvelus-tech/rank-rent-niches"
TOKEN=$(gh auth status -t 2>/dev/null | grep -o 'gho_[a-zA-Z0-9]*' || echo "")

curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/${REPO}/pages \
  -d '{"source":{"branch":"main","path":"/"}}'