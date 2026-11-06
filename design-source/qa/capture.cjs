// Capture one board: screenshot plus a content fingerprint, optionally after interaction steps.
//
// Usage: node capture.cjs <projectDir> <board> <w> <h> <outPrefix> [stepsJsonFile]
// Steps: [{"click":"<playwright selector>"},{"fill":["<selector>","text"]},{"scrollTo":1200},{"wait":400},{"key":"Escape"}]
// Writes <outPrefix>.png and <outPrefix>.json
const http = require('http');
const fs = require('fs');
const path = require('path');
const { createRequire } = require('module');
const { execSync } = require('child_process');

const groot = execSync('npm root -g').toString().trim();
const req = createRequire(path.join(groot, '@playwright/cli/package.json'));
const { chromium } = req('playwright');

const [projectDir, board, w, h, outPrefix, stepsFile] = process.argv.slice(2);
const RUNTIME = process.env.DC_RUNTIME;
const steps = stepsFile ? JSON.parse(fs.readFileSync(stepsFile, 'utf8')) : [];
fs.mkdirSync(path.dirname(outPrefix), { recursive: true });
const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json' };

function placeholder(id) {
  const n = parseInt(id.slice(0, 6), 16) || 0;
  const hue = n % 360;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600"><rect width="800" height="600" fill="hsl(${hue} 30% 72%)"/><path d="M0 600L400 300 800 600z" fill="hsl(${hue} 30% 55%)"/></svg>`;
}

const server = http.createServer((q, s) => {
  const u = decodeURIComponent(q.url.split('?')[0]);
  if (u.endsWith('/support.js')) {
    s.writeHead(200, { 'content-type': MIME['.js'] });
    return s.end(fs.readFileSync(RUNTIME));
  }
  const blob = u.match(/\/_blob\/([0-9a-f]+)/);
  if (blob) {
    const realDir = process.env.REAL_IMAGES;
    if (realDir) {
      const hit = fs.readdirSync(realDir).find((f) => f.startsWith(blob[1] + '.'));
      if (hit) {
        const types = { '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml', '.gif': 'image/gif' };
        s.writeHead(200, { 'content-type': types[path.extname(hit)] || 'application/octet-stream' });
        return s.end(fs.readFileSync(path.join(realDir, hit)));
      }
    }
    s.writeHead(200, { 'content-type': 'image/svg+xml' });
    return s.end(placeholder(blob[1]));
  }
  const file = path.join(projectDir, u.replace(/^\/+/, ''));
  if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    s.writeHead(404);
    return s.end('');
  }
  s.writeHead(200, { 'content-type': MIME[path.extname(file)] || 'application/octet-stream' });
  s.end(fs.readFileSync(file));
});

const NOISE = /fonts\.g|ERR_|Failed to load resource|<svg> attribute|<path> attribute|<circle> attribute|<rect> attribute|<stop> attribute|<line> attribute|<ellipse> attribute|<g> attribute|<polyline> attribute/;

(async () => {
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  const port = server.address().port;
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: Number(w), height: Number(h) }, reducedMotion: 'reduce', deviceScaleFactor: 1 });
  await ctx.addInitScript(() => {
    const fixed = new Date('2026-11-03T10:00:00+07:00').getTime();
    const D = Date;
    class FD extends D {
      constructor(...a) { if (a.length) super(...a); else super(fixed); }
      static now() { return fixed; }
    }
    window.Date = FD;
    let s = 42;
    Math.random = () => (s = (s * 16807) % 2147483647) / 2147483647;
    // Freeze autoplay so carousels cannot change between the two renders.
    const si = window.setInterval.bind(window);
    window.setInterval = (fn, ms, ...a) => (ms >= 1500 ? 0 : si(fn, ms, ...a));
  });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + String(e.message).slice(0, 300)));
  page.on('console', (m) => {
    if (m.type() === 'error' || (m.type() === 'warning' && m.text().includes('dc-runtime'))) {
      const t = m.text();
      if (!NOISE.test(t)) errors.push(m.type() + ': ' + t.slice(0, 300));
    }
  });
  await page.goto(`http://127.0.0.1:${port}/${board}.dc.html`, { waitUntil: 'load', timeout: 60000 });
  await page.waitForTimeout(Number(process.env.SETTLE_MS || 2000));
  // Lazy images load at random times, which made identical boards differ. Load them all, on both sides.
  const loadAll = () => page.evaluate(async () => {
    const imgs = [...document.querySelectorAll('img')];
    imgs.forEach((i) => { if (i.loading === 'lazy') i.loading = 'eager'; });
    await Promise.race([Promise.all(imgs.map((i) => (i.complete ? null : new Promise((r) => { i.onload = r; i.onerror = r; })))), new Promise((r) => setTimeout(r, 4000))]);
  });
  await loadAll();
  await page.waitForTimeout(300);
  for (const st of steps) {
    if (st.click) await page.locator(st.click).first().click({ timeout: 8000, force: !!st.force });
    if (st.fill) await page.locator(st.fill[0]).first().fill(st.fill[1], { timeout: 8000 });
    if (st.scrollTo !== undefined) await page.evaluate((y) => window.scrollTo(0, y), st.scrollTo);
    if (st.eval) await page.evaluate(st.eval);
    if (st.key) await page.keyboard.press(st.key);
    await page.waitForTimeout(st.wait ?? 500);
  }
  await loadAll();
  // Boards with web fonts re-measure spacing once the fonts arrive; wait for that before reading the page height.
  await page.evaluate(() => (document.fonts ? document.fonts.ready : null));
  await page.waitForTimeout(600);
  const fp = await page.evaluate(() => {
    const visible = (el) => {
      const s = getComputedStyle(el);
      if (s.visibility === 'hidden' || s.display === 'none' || Number(s.opacity) === 0) return false;
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0;
    };
    const texts = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = walker.nextNode())) {
      const t = n.nodeValue.replace(/\s+/g, ' ').trim();
      if (!t) continue;
      const el = n.parentElement;
      if (!el || ['SCRIPT', 'STYLE', 'TITLE'].includes(el.tagName) || !visible(el)) continue;
      const s = getComputedStyle(el);
      texts.push({ t: t.slice(0, 120), fs: s.fontSize, c: s.color, w: s.fontWeight, ff: s.fontFamily.split(',')[0].replace(/"/g, ''), lh: s.lineHeight, ls: s.letterSpacing, tt: s.textTransform });
    }
    const all = [...document.body.querySelectorAll('*')];
    const hrefs = all.filter((e) => e.tagName === 'A' && e.getAttribute('href') && visible(e)).map((e) => e.getAttribute('href'));
    const imgs = all.filter((e) => e.tagName === 'IMG' && visible(e)).map((e) => e.getAttribute('src'));
    const bgs = all.filter(visible).map((e) => (getComputedStyle(e).backgroundImage.match(/\/_blob\/[0-9a-f]+/) || [])[0]).filter(Boolean);
    const lm = all.filter((e) => ['MAIN', 'NAV', 'HEADER', 'FOOTER', 'H1', 'H2', 'H3'].includes(e.tagName) && visible(e)).map((e) => e.tagName);
    return {
      width: document.documentElement.scrollWidth,
      height: Math.max(document.documentElement.scrollHeight, document.body.scrollHeight),
      elements: all.length,
      logicErrors: [...document.querySelectorAll('.sc-logic-error')].map((e) => e.textContent.slice(0, 300)),
      texts, hrefs, imgs, bgs, landmarks: lm,
    };
  });
  await page.screenshot({ path: outPrefix + '.png', fullPage: true, animations: 'disabled', timeout: 90000 });
  fs.writeFileSync(outPrefix + '.json', JSON.stringify({ ...fp, errors }));
  await browser.close();
  server.close();
})().catch((e) => {
  console.error('CAPTURE FAILED: ' + e.message);
  process.exit(2);
});
