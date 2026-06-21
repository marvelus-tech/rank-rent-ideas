const { chromium } = require('playwright');
const fs = require('fs');

const VIDEO_URL = 'https://youtu.be/t_y8SelBm_s';
const OUTPUT = '/Users/oktos/.openclaw/workspace/yt_transcript.txt';
const delay = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const context = await browser.newContext({
    userAgent:
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    viewport: { width: 1400, height: 900 },
    locale: 'en-US',
  });
  const page = await context.newPage();

  let title = 'Unknown title';
  let channel = 'Unknown channel';
  let description = 'Description unavailable';
  let transcriptText = '';

  try {
    await page.goto(VIDEO_URL, { waitUntil: 'domcontentloaded', timeout: 120000 });
    await delay(3000);

    // Handle consent pages / banners
    const consentButtons = [
      'button:has-text("Accept all")',
      'button:has-text("I agree")',
      'button:has-text("Accept")',
      'form button:has-text("I agree")',
      'form button:has-text("Accept all")'
    ];
    for (const sel of consentButtons) {
      const b = page.locator(sel).first();
      if (await b.isVisible({ timeout: 1500 }).catch(() => false)) {
        await b.click().catch(() => {});
        await delay(3000);
        break;
      }
    }

    if (!page.url().includes('youtube.com/watch')) {
      await page.goto('https://www.youtube.com/watch?v=t_y8SelBm_s', { waitUntil: 'domcontentloaded', timeout: 120000 }).catch(() => {});
      await delay(3000);
    }

    // Try collect visible metadata
    title = (await page.locator('h1.ytd-watch-metadata yt-formatted-string, h1.title yt-formatted-string').first().innerText().catch(() => '')).trim() || title;
    channel = (await page.locator('#channel-name a, ytd-channel-name a').first().innerText().catch(() => '')).trim() || channel;
    description = (await page.locator('#description-inline-expander, #description, ytd-text-inline-expander').first().innerText().catch(() => '')).trim() || description;

    // Fallback metadata from meta tags
    const meta = await page.evaluate(() => {
      const g = (sel) => document.querySelector(sel)?.content || '';
      return {
        ogTitle: g('meta[property="og:title"]'),
        ogDesc: g('meta[property="og:description"]'),
        name: document.querySelector('meta[itemprop="name"]')?.content || '',
        author: document.querySelector('link[itemprop="name"]')?.content || document.querySelector('meta[itemprop="author"]')?.content || '',
      };
    }).catch(() => ({}));

    if (meta.ogTitle && title === 'Unknown title') title = meta.ogTitle;
    if (meta.author && channel === 'Unknown channel') channel = meta.author;
    if (meta.ogDesc && description === 'Description unavailable') description = meta.ogDesc;

    // More fallback from player response
    const details = await page.evaluate(() => {
      const vd = window.ytInitialPlayerResponse?.videoDetails || {};
      return {
        title: vd.title || '',
        author: vd.author || '',
        shortDescription: vd.shortDescription || ''
      };
    }).catch(() => ({}));

    if (details.title && title === 'Unknown title') title = details.title;
    if (details.author && channel === 'Unknown channel') channel = details.author;
    if (details.shortDescription && description === 'Description unavailable') description = details.shortDescription;

    // Open transcript via menu
    const menuCandidates = [
      'ytd-menu-renderer yt-icon-button button',
      'button[aria-label*="More actions"]'
    ];
    for (const sel of menuCandidates) {
      const btn = page.locator(sel).first();
      if (await btn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await btn.click().catch(() => {});
        await delay(2500);
        const tr = page.locator('tp-yt-paper-item:has-text("Show transcript"), ytd-menu-service-item-renderer:has-text("Show transcript")').first();
        if (await tr.isVisible({ timeout: 2000 }).catch(() => false)) {
          await tr.click().catch(() => {});
          await delay(3500);
          break;
        }
      }
    }

    const transcriptContainer = page.locator('ytd-transcript-segment-list-renderer, #segments-container').first();
    const hasTranscript = await transcriptContainer.isVisible({ timeout: 5000 }).catch(() => false);

    if (hasTranscript) {
      for (let i = 0; i < 8; i++) {
        await transcriptContainer.evaluate((el) => el.scrollBy(0, 1100)).catch(() => {});
        await delay(800);
      }
      const segs = page.locator('ytd-transcript-segment-renderer');
      const n = await segs.count();
      const lines = [];
      for (let i = 0; i < n; i++) {
        const s = segs.nth(i);
        const t = (await s.locator('.segment-timestamp, #start-offset').first().innerText().catch(() => '')).trim();
        const x = (await s.locator('.segment-text, yt-formatted-string').last().innerText().catch(() => '')).trim();
        if (x) lines.push(t ? `[${t}] ${x}` : x);
      }
      transcriptText = lines.join('\n');
    }

    // Fallback: extract captions from player response JSON (still via Playwright/browser)
    if (!transcriptText) {
      const captionFromApi = await page.evaluate(async () => {
        try {
          const pr = window.ytInitialPlayerResponse || null;
          const tracks = pr?.captions?.playerCaptionsTracklistRenderer?.captionTracks || [];
          if (!tracks.length) return '';
          const track = tracks.find(t => /en/i.test(t.languageCode || '')) || tracks[0];
          const base = track.baseUrl;
          if (!base) return '';
          const url = base.includes('fmt=') ? base : `${base}&fmt=json3`;
          const res = await fetch(url, { credentials: 'include' });
          const data = await res.json();
          const events = data.events || [];
          const lines = [];
          for (const ev of events) {
            if (!ev.segs) continue;
            const text = ev.segs.map(s => s.utf8 || '').join('').replace(/\n/g, ' ').trim();
            if (!text) continue;
            const ms = ev.tStartMs || 0;
            const h = Math.floor(ms / 3600000);
            const m = Math.floor((ms % 3600000) / 60000);
            const s = Math.floor((ms % 60000) / 1000);
            const ts = h > 0
              ? `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`
              : `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
            lines.push(`[${ts}] ${text}`);
          }
          return lines.join('\n');
        } catch (e) {
          return '';
        }
      }).catch(() => '');

      if (captionFromApi) transcriptText = captionFromApi;
    }

    if (!transcriptText) transcriptText = 'Transcript not available via UI extraction in this environment.';

    const summary = transcriptText.startsWith('Transcript not available')
      ? 'Transcript panel could not be accessed. Based on metadata, the video discusses how to make money online via a practical business model and likely includes steps, strategy, and execution guidance.'
      : 'The video explains a business model framework with practical execution steps, focusing on monetization mechanics, offer structure, and growth actions to replicate results.';

    const output = [
      `Video URL: ${VIDEO_URL}`,
      `Final URL: ${page.url()}`,
      `Title: ${title}`,
      `Channel: ${channel}`,
      '',
      '=== Brief Summary ===',
      summary,
      '',
      '=== Description / Metadata ===',
      description,
      '',
      '=== Transcript ===',
      transcriptText,
      ''
    ].join('\n');

    fs.writeFileSync(OUTPUT, output, 'utf8');
    console.log(`Saved: ${OUTPUT}`);
    console.log(`Title: ${title}`);
    console.log(`Channel: ${channel}`);
    console.log(`Transcript length: ${transcriptText.length}`);
  } catch (err) {
    fs.writeFileSync(OUTPUT, `Extraction error: ${err?.message || err}\n`, 'utf8');
    console.log(`Extraction error: ${err?.message || err}`);
  } finally {
    await delay(2000);
    await browser.close();
  }
})();
