#!/usr/bin/env python3
"""
Playwright-based Google Maps Lead Scraper (No Vision Required)
===============================================================
Alternative to Peekaboo scraper that uses Playwright browser automation.
Extracts business data directly from the search results list without clicking.

Usage:
    python3 playwright_maps_scraper.py "mechanics" "Victoria, Australia" --limit 10
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

UTC = timezone.utc


def scrape_maps_playwright(category: str, location: str, limit: int = 10):
    """Scrape Google Maps using Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright not installed. Install with: pip install playwright")
        print("   Then run: playwright install chromium")
        return []
    
    leads = []
    search_query = f"{category} {location}"
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        page = context.new_page()
        
        # Navigate to Google Maps
        print(f"🔍 Searching: {search_query}")
        page.goto(f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}")
        
        # Wait for results to load
        print("   Waiting for results...")
        time.sleep(5)
        
        # Extract business listings directly from the results list
        print("   Extracting business data...")
        
        # Use JavaScript to extract structured data from the page
        js_code = """
        () => {
            const results = [];
            const cards = document.querySelectorAll('[data-result-index], .bfdHYd, [role="feed"] > div');
            
            cards.forEach((card) => {
                try {
                    // Get business name
                    let name = '';
                    const nameEl = card.querySelector('h3, .qBF1Pd');
                    if (nameEl) {
                        name = nameEl.textContent.trim();
                    }
                    
                    if (!name || name.length < 2) return;
                    
                    // Get all text and split into lines
                    const cardText = card.innerText || '';
                    const lines = cardText.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                    
                    // Extract phone
                    let phone = '';
                    const phonePatterns = [
                        /\\+?61[\\s\\-]?\\d[\\s\\-]?\\d{4}[\\s\\-]?\\d{4}/,
                        /\\d{4}[\\s\\-]?\\d{3}[\\s\\-]?\\d{3}/,
                        /\\d{2}[\\s\\-]?\\d{4}[\\s\\-]?\\d{4}/,
                        /\\(\\d{3}\\)\\s*\\d{3}[\\s\\-]?\\d{4}/
                    ];
                    for (const pattern of phonePatterns) {
                        const match = cardText.match(pattern);
                        if (match) {
                            phone = match[0];
                            break;
                        }
                    }
                    
                    // Extract rating
                    let rating = '';
                    const ratingMatch = cardText.match(/(\\d\\.\\d)\\s*\\(?\\d*\\)?/);
                    if (ratingMatch) {
                        rating = ratingMatch[1];
                    }
                    
                    // Extract address
                    let address = '';
                    for (const line of lines) {
                        if (line.match(/\\d+.*\\b(Rd|St|Ave|Blvd|Dr|Ln|Way|Highway|Hwy|Road|Street|Avenue|Pl|Court|Ct)\\b/i)) {
                            address = line;
                            break;
                        }
                    }
                    
                    // Check if open
                    const isOpen = cardText.includes('Open') && !cardText.includes('Closed');
                    
                    results.push({
                        name: name,
                        text: cardText.substring(0, 200),
                        phone: phone,
                        rating: rating,
                        address: address,
                        is_open: isOpen
                    });
                } catch (e) {}
            });
            
            return results;
        }
        """
        
        businesses = page.evaluate(js_code)
        
        # Deduplicate by name
        seen_names = set()
        unique_businesses = []
        for biz in businesses:
            if biz['name'] not in seen_names:
                seen_names.add(biz['name'])
                unique_businesses.append(biz)
        
        businesses = unique_businesses
        
        print(f"📍 Found {len(businesses)} unique businesses")
        
        for biz in businesses[:limit]:
            # Score the lead
            score = 50  # Base score
            missing = []
            
            if not biz['phone']:
                missing.append('phone')
            else:
                score += 15
            
            if not biz['address']:
                missing.append('address')
            else:
                score += 10
            
            if not biz['rating']:
                missing.append('rating')
            else:
                score += 10
            
            if biz['is_open']:
                score += 5
            
            # Determine priority
            if score >= 75:
                priority = "HOT"
            elif score >= 50:
                priority = "WARM"
            else:
                priority = "COLD"
            
            lead = {
                'name': biz['name'],
                'category': category,
                'location': location,
                'phone': biz['phone'],
                'address': biz['address'],
                'rating': biz['rating'],
                'is_open': biz['is_open'],
                'score': min(score, 100),
                'priority': priority,
                'missing': missing,
                'source': 'google_maps_playwright',
                'scraped_at': datetime.now(UTC).isoformat()
            }
            
            leads.append(lead)
            print(f"  ✓ {biz['name']} (Score: {score}, {priority})")
        
        browser.close()
    
    return leads


def save_leads(leads: list, category: str, location: str):
    """Save leads to JSON and CSV."""
    timestamp = datetime.now(UTC).strftime('%Y-%m-%d_%H%M%S')
    
    # Save to processed
    processed_dir = Path('data/processed')
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    json_file = processed_dir / f'playwright_leads_{timestamp}.json'
    with open(json_file, 'w') as f:
        json.dump({
            'category': category,
            'location': location,
            'generated_at': datetime.now(UTC).isoformat(),
            'count': len(leads),
            'leads': leads
        }, f, indent=2)
    
    # Save to CSV
    csv_file = processed_dir / f'playwright_leads_{timestamp}.csv'
    import csv
    with open(csv_file, 'w', newline='') as f:
        if leads:
            writer = csv.DictWriter(f, fieldnames=leads[0].keys())
            writer.writeheader()
            writer.writerows(leads)
    
    print(f"\n💾 Saved {len(leads)} leads to:")
    print(f"   JSON: {json_file}")
    print(f"   CSV: {csv_file}")


def main():
    parser = argparse.ArgumentParser(description='Playwright Maps Scraper')
    parser.add_argument('category', help='Business category (e.g., mechanics)')
    parser.add_argument('location', help='Location (e.g., "Victoria, Australia")')
    parser.add_argument('--limit', type=int, default=10, help='Max leads to scrape')
    
    args = parser.parse_args()
    
    print(f"🚀 Playwright Maps Scraper")
    print(f"   Category: {args.category}")
    print(f"   Location: {args.location}")
    print(f"   Limit: {args.limit}")
    print()
    
    leads = scrape_maps_playwright(args.category, args.location, args.limit)
    
    if leads:
        save_leads(leads, args.category, args.location)
        
        # Summary
        hot = sum(1 for l in leads if l['priority'] == 'HOT')
        warm = sum(1 for l in leads if l['priority'] == 'WARM')
        cold = sum(1 for l in leads if l['priority'] == 'COLD')
        
        print(f"\n📊 Summary:")
        print(f"   HOT: {hot} | WARM: {warm} | COLD: {cold}")
        print(f"\n✅ Success: {len(leads)} leads scraped")
    else:
        print("\n❌ No leads found")
        sys.exit(1)


if __name__ == '__main__':
    main()
