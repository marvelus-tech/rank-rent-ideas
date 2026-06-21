"""
Obsidian-based duplicate tracking for marketplace listings.
Replaces SQLite with Obsidian notes for tracking seen listings.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class ObsidianTracker:
    """Track seen listings using Obsidian notes instead of SQLite."""
    
    def __init__(self, vault_path: Optional[str] = None):
        # Auto-detect vault path if not provided
        if vault_path is None:
            vault_path = self._detect_vault_path()
        self.vault_path = Path(vault_path)
        self.listings_dir = self.vault_path / "Listings"
        self.listings_dir.mkdir(parents=True, exist_ok=True)
    
    def _detect_vault_path(self) -> str:
        """Detect the default Obsidian vault path."""
        try:
            result = subprocess.run(
                ["obsidian-cli", "print-default", "--path-only"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
        
        # Fallback to default location
        return "/Users/oktos/Documents/Obsidian Vaults/MarketplaceScraper"
    
    def _listing_id(self, url: str) -> str:
        """Generate a consistent ID from listing URL."""
        # Use MD5 hash of URL for filename (safe for filesystem)
        return hashlib.md5(url.encode()).hexdigest()[:12]
    
    def _listing_path(self, listing_id: str) -> Path:
        """Get the path to a listing note."""
        return self.listings_dir / f"{listing_id}.md"
    
    def has_seen(self, url: str) -> bool:
        """Check if we've already seen this listing."""
        listing_id = self._listing_id(url)
        return self._listing_path(listing_id).exists()
    
    def get_seen_urls(self) -> Set[str]:
        """Get all previously seen listing URLs from the vault."""
        seen = set()
        if not self.listings_dir.exists():
            return seen
            
        for note_path in self.listings_dir.glob("*.md"):
            try:
                content = note_path.read_text(encoding="utf-8")
                # Extract URL from frontmatter
                match = re.search(r'^url:\s*(.+)$', content, re.MULTILINE)
                if match:
                    seen.add(match.group(1).strip())
            except Exception:
                continue
        return seen
    
    def mark_seen(self, listing: Dict[str, Any]) -> bool:
        """
        Mark a listing as seen by creating an Obsidian note.
        Returns True if this was a new listing, False if already seen.
        """
        url = listing.get("url", "")
        if not url:
            return False
            
        listing_id = self._listing_id(url)
        note_path = self._listing_path(listing_id)
        
        # Already seen
        if note_path.exists():
            return False
        
        # Create the note with frontmatter
        title = listing.get("title", "Unknown Item")
        price = listing.get("price_raw") or listing.get("price", "N/A")
        location = listing.get("location", "")
        
        note_content = f"""---
url: {url}
first_seen: {datetime.now().isoformat()}
last_seen: {datetime.now().isoformat()}
price: {price}
location: {location}
status: tracked
---

# {title}

**Price:** {price}
**Location:** {location}
**URL:** {url}

## Details

```json
{json.dumps(listing, indent=2, default=str)}
```

## Notes

- First detected: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Price History

| Date | Price | Notes |
|------|-------|-------|
| {datetime.now().strftime("%Y-%m-%d")} | {price} | Initial detection |
"""
        
        note_path.write_text(note_content, encoding="utf-8")
        return True
    
    def update_listing(self, url: str, updates: Dict[str, Any]) -> bool:
        """Update an existing listing note with new information."""
        listing_id = self._listing_id(url)
        note_path = self._listing_path(listing_id)
        
        if not note_path.exists():
            return False
        
        content = note_path.read_text(encoding="utf-8")
        
        # Update last_seen timestamp
        content = re.sub(
            r'^last_seen:.*$',
            f'last_seen: {datetime.now().isoformat()}',
            content,
            flags=re.MULTILINE
        )
        
        # If price changed, add to price history
        if "price" in updates:
            new_price = updates["price"]
            price_line = f"| {datetime.now().strftime('%Y-%m-%d')} | {new_price} | Price update |"
            # Add before the end of the price history table
            content = content.replace(
                "|------|-------|-------|",
                f"|------|-------|-------|\n{price_line}"
            )
        
        note_path.write_text(content, encoding="utf-8")
        return True
    
    def filter_new_listings(self, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter a list of listings to only return new (unseen) ones."""
        new_listings = []
        for listing in listings:
            url = listing.get("url", "")
            if url and not self.has_seen(url):
                new_listings.append(listing)
        return new_listings
    
    def get_stats(self) -> Dict[str, int]:
        """Get tracking statistics."""
        if not self.listings_dir.exists():
            return {"total_tracked": 0}
        
        total = len(list(self.listings_dir.glob("*.md")))
        return {"total_tracked": total}


def get_tracker(vault_path: Optional[str] = None) -> ObsidianTracker:
    """Factory function to get a tracker instance."""
    return ObsidianTracker(vault_path)
