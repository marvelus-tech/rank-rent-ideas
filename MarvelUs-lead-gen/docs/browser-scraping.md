# Browser Scraping Mode (Google Maps, no APIs)

This mode uses Playwright to automate a real browser against Google Maps.

## Why use it

- No API keys
- Zero per-request API cost
- Same downstream pipeline as API mode (dedupe, contact extraction, scoring, reports)

## Command

```bash
python main.py run --config config/config.yaml --mode browser
```

## Configuration

```yaml
browser:
  headless: true
  slow_mo: 2000
  max_results_per_search: 30
  search_delay_seconds: 5
```

## Data captured per listing

- name
- address
- phone
- website
- rating
- reviews
- business_hours
- business_type

## Failure handling

- Retries with exponential backoff for transient browser failures
- CAPTCHA detection halts current query and saves debug artifacts
- Query-level errors are skipped so remaining categories/locations continue

## Debug artifacts

Saved in `data/debug/browser/`:
- Raw HTML snapshot
- Full-page screenshot
- Error log text
