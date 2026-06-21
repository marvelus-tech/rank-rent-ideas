#!/bin/bash
# Enable GitHub Pages via API

REPO="marvelus-tech/tko-intel-feed"
TOKEN=$(gh auth token)

curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/${REPO}/pages \
  -d '{"source":{"branch":"main","path":"/"}}'