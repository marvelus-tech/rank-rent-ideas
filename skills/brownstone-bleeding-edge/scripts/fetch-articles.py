import json
import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

BLEEDING_EDGE_URL = "https://www.brownstoneresearch.com/bleeding-edge/"

def fetch_articles():
    """Fetch all articles from the Bleeding Edge page."""
    # Using openclaw web_fetch tool is more reliable than requests direct if they block
    # But for a script, we'll try to simulate the web_fetch behavior or just use it if we can
    # Since this is a script, we'll use requests with headers first, then fallback to a mock if needed.
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(BLEEDING_EDGE_URL, headers=headers, timeout=30)
        
        # If blocked (403), we can't easily fix it here without playwright/selenium 
        # but we know web_fetch worked. Let's provide a way to use web_fetch output.
        if response.status_code == 403:
             # Fallback: if we are running in an environment with openclaw tools, we'd use them
             # For now, let's try to extract from the raw response anyway in case it was a fluke
             pass
             
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        seen_urls = set()
        
        for h3 in soup.find_all('h3'):
            link = h3.find('a', href=True)
            if not link: continue
            href = link['href']
            if '/page/' in href: continue
            if not href.startswith('/bleeding-edge/') and not href.startswith('https://www.brownstoneresearch.com/bleeding-edge/'): continue
            if href == '/bleeding-edge/' or href == BLEEDING_EDGE_URL: continue
            
            full_url = urljoin(BLEEDING_EDGE_URL, href)
            if full_url in seen_urls: continue
            seen_urls.add(full_url)
            
            title = h3.get_text(strip=True)
            slug = href.strip('/').split('/')[-1]
            
            date = ""
            excerpt = ""
            next_elem = h3.find_next_sibling()
            if next_elem:
                text = next_elem.get_text(strip=True)
                if re.match(r'[A-Za-z]{3}\s+\d{1,2},\s+\d{4}', text):
                    date = text
                    excerpt_elem = next_elem.find_next_sibling()
                    if excerpt_elem:
                        excerpt = excerpt_elem.get_text(strip=True)
                else:
                    excerpt = text
                    parent = h3.parent
                    if parent:
                        parent_text = parent.get_text()
                        date_match = re.search(r'([A-Za-z]{3}\s+\d{1,2},\s+\d{4})', parent_text)
                        if date_match:
                            date = date_match.group(1)
            
            articles.append({
                'url': full_url,
                'slug': slug,
                'title': title,
                'date': date,
                'excerpt': excerpt
            })
        
        return articles
    
    except Exception as e:
        # If we failed, check if we have a cached version from web_fetch or similar
        print(f"Error fetching articles: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Check if we have piped input (e.g. from web_fetch)
    if not sys.stdin.isatty():
        # Try to parse markdown from web_fetch
        raw_input = sys.stdin.read()
        try:
            # Simple regex to find links in the markdown returned by web_fetch
            # Format: ### [Title](URL) \n\n Excerpt \n\n Date
            articles = []
            seen_urls = set()
            
            # Pattern for: ### [Title](URL)
            matches = re.finditer(r'### \[(.*?)\]\((https://www\.brownstoneresearch\.com/bleeding-edge/.*?/)\)', raw_input)
            for match in matches:
                title = match.group(1)
                url = match.group(2)
                
                if url in seen_urls: continue
                seen_urls.add(url)
                
                slug = url.strip('/').split('/')[-1]
                
                # Try to find date nearby (usually follows the link)
                # Look for "Apr 15, 2026" style dates
                start_pos = match.end()
                nearby_text = raw_input[start_pos:start_pos+500]
                date_match = re.search(r'([A-Za-z]{3}\s+\d{1,2},\s+\d{4})', nearby_text)
                date = date_match.group(1) if date_match else ""
                
                articles.append({
                    'url': url,
                    'slug': slug,
                    'title': title,
                    'date': date,
                    'excerpt': "" # Harder to extract cleanly from MD without better parsing
                })
            
            if articles:
                print(json.dumps(articles, indent=2))
                sys.exit(0)
        except Exception:
            pass

    articles = fetch_articles()
    print(json.dumps(articles, indent=2))
