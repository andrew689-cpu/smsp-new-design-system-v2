// Render .dc.html boards locally with the real dc-runtime and take full-page screenshots.
//
// Usage: node render.cjs <projectDir> <outDir> <width> <height> <Board> [<Board> ...]
//   Board may be "Name" or "Name:propsJSON" is NOT supported; boards render with their defaults.
// Prints one JSON line per board: {board, ok, width, height, errors, logicErrors, missing}
//
// /support.js  -> the real dc-runtime.js
// /_blob/<id>  -> a deterministic placeholder (color from id), so both sides of a comparison match.
const http = require('http');
const fs = require('fs');
const path = require('path');
const { createRequire } = require('module');
const { execSync } = require('child_process');

const groot = execSync('npm root -g').toString().trim();
const req = createRequire(path.join(groot, '@playwright/cli/package.json'));
const { chromium } = req('playwright');

const [projectDir, outDir, widthArg, heightArg, ...boards] = process.argv.slice(2);
const RUNTIME = process.env.DC_RUNTIME;
const width = Number(widthArg);
const height = Number(heightArg);
fs.mkdirSync(outDir, { recursive: true });

const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json' };

function placeholder(id) {
  const n = parseInt(id.slice(0, 6), 16) || 0;
  const hue = n % 360;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600"><rect width="800" height="600" fill="hsl(${hue} 30% 72%)"/><path d="M0 600L400 300 800 600z" fill="hsl(${hue} 30% 55%)"/></svg>`;
}

const missing = new Set();
const server = http.createServer((q, s) => {
  const u = decodeURIComponent(q.url.split('?')[0]);
  if (u.endsWith('/support.js')) {
    s.writeHead(200, { 'content-type': MIME['.js'] });
    return s.end(fs.readFileSync(RUNTIME));
  }
  const blob = u.match(/\/_blob\/([0-9a-f]+)/);
  if (blob) {
    s.writeHead(200, { 'content-type': 'image/svg+xml' });
    return s.end(placeholder(blob[1]));
  }
  const file = path.join(projectDir, u.replace(/^\/+/, ''));
  if (!file.startsWith(path.resolve(projectDir)) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    missing.add(u);
    s.writeHead(404);
    return s.end('');
  }
  s.writeHead(200, { 'content-type': MIME[path.extname(file)] || 'application/octet-stream' });
  s.end(fs.readFileSync(file));
});

(async () => {
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  const port = server.address().port;
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width, height }, reducedMotion: 'reduce', deviceScaleFactor: 1 });
  // Fix the clock so office-hours and date logic match between runs.
  await ctx.addInitScript(() => {
    const fixed = new Date('2026-11-03T10:00:00+07:00').getTime();
    const D = Date;
    class FD extends D {
      constructor(...a) { if (a.length) super(...a); else super(fixed); }
      static now() { return fixed; }
    }
    window.Date = FD;
    Math.random = (() => { let s = 42; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();
  });
  let bad = 0;
  for (const board of boards) {
    missing.clear();
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push('pageerror: ' + String(e.message).slice(0, 240)));
    page.on('console', (m) => {
      if (m.type() === 'error' || (m.type() === 'warning' && m.text().includes('dc-runtime'))) {
        const t = m.text();
        if (!/fonts\.g|ERR_|Failed to load resource|<svg> attribute|<path> attribute|<circle> attribute|<rect> attribute/.test(t)) errors.push(m.type() + ': ' + t.slice(0, 240));
      }
    });
    let result = { board, ok: false };
    try {
      await page.goto(`http://127.0.0.1:${port}/${board}.dc.html`, { waitUntil: 'load', timeout: 45000 });
      await page.waitForTimeout(Number(process.env.SETTLE_MS || 1800));
      const info = await page.evaluate(() => {
        const q = (s) => [...document.querySelectorAll(s)];
        return {
          logicErrors: q('.sc-logic-error').map((e) => e.textContent.slice(0, 240)),
          placeholders: q('.sc-unresolved').length,
          width: document.documentElement.scrollWidth,
          height: Math.max(document.documentElement.scrollHeight, document.body.scrollHeight),
          text: document.body.innerText.length,
          elements: document.body.getElementsByTagName('*').length,
          hasRootVar: getComputedStyle(document.documentElement).getPropertyValue('--brand').trim(),
        };
      });
      await page.screenshot({ path: path.join(outDir, board + '.png'), fullPage: true, animations: 'disabled', timeout: 60000 });
      result = { board, ok: info.logicErrors.length === 0 && errors.length === 0, ...info, errors, missing: [...missing] };
    } catch (e) {
      result = { board, ok: false, fatal: String(e.message).slice(0, 300), errors, missing: [...missing] };
    }
    if (!result.ok) bad++;
    console.log(JSON.stringify(result));
    await page.close();
  }
  await browser.close();
  server.close();
  process.exit(bad ? 1 : 0);
})();
