import json
import sys
import os
import requests
from bs4 import BeautifulSoup
import re

def fetch_article_content(url):
    """Fetch full article content from URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        # If blocked, try to parse from web_fetch output if piped in
        if response.status_code == 403:
             # Logic to handle piped markdown from web_fetch
             pass
             
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = ""
        title_elem = soup.find('h1') or soup.find('h2')
        if title_elem:
            title = title_elem.get_text(strip=True)
        
        content = ""
        content_selectors = ['main', '.entry-content', '.post-content', '.content-area', 'article', '[class*="content"]']
        
        content_elem = None
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                break
        
        if content_elem:
            paragraphs = content_elem.find_all('p')
            content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        if not content:
            paragraphs = soup.find_all('p')
            content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
        
        date = ""
        date_elem = soup.find('time') or soup.find(class_=re.compile(r'date|time', re.I))
        if date_elem:
            date = date_elem.get_text(strip=True)
        
        article_data = {
            'url': url,
            'title': title,
            'date': date,
            'slug': url.strip('/').split('/')[-1],
            'content': content,
            'word_count': len(content.split())
        }
        
        return article_data
    
    except Exception as e:
        # Fallback for piped web_fetch markdown
        if not sys.stdin.isatty():
             raw_input = sys.stdin.read()
             try:
                 # Check if markdown from web_fetch contains the correct article URL
                 if url in raw_input or f"({url})" in raw_input:
                     # Very simple extraction: everything after first title until footer links
                     # Title is usually the first header or provided in web_fetch 'title' field
                     # We'll just take the whole text minus some known boilerplate
                     content = raw_input.split("---")[-1] if "---" in raw_input else raw_input
                     content = content.split("<<<END_EXTERNAL_UNTRUSTED_CONTENT")[0]
                     
                     article_data = {
                        'url': url,
                        'title': "Article from Web Fetch", # Hard to extract without full parser
                        'date': "",
                        'content': content.strip(),
                        'word_count': len(content.split())
                     }
                     return article_data
             except Exception:
                 pass
                 
        print(f"Error fetching article: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fetch-article-content.py <article-url>", file=sys.stderr)
        sys.exit(1)
    
    url = sys.argv[1]
    article = fetch_article_content(url)
    print(json.dumps(article, indent=2))
