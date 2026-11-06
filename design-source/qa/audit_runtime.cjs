// Propagation audit. Plants a hidden marker in every component FILE, renders every screen with the
// real runtime, and records which markers arrive and who owns each visible element.
// Usage: node audit_runtime.cjs <projectDir> <screensJson> <outJson>
const http = require('http');
const fs = require('fs');
const path = require('path');
const { createRequire } = require('module');
const { execSync } = require('child_process');
const groot = execSync('npm root -g').toString().trim();
const req = createRequire(path.join(groot, '@playwright/cli/package.json'));
const { chromium } = req('playwright');
const [projectDir, screensFile, outFile] = process.argv.slice(2);
const screens = JSON.parse(fs.readFileSync(screensFile, 'utf8'));
const shot = new Set(screens);
const realDir = process.env.REAL_IMAGES;
const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg' };
const server = http.createServer((q, s) => {
  const u = decodeURIComponent(q.url.split('?')[0]);
  if (u.endsWith('/support.js')) { s.writeHead(200, { 'content-type': MIME['.js'] }); return s.end(fs.readFileSync(process.env.DC_RUNTIME)); }
  const blob = u.match(/\/_blob\/([0-9a-f]+)/);
  if (blob) {
    const hit = fs.readdirSync(realDir).find((f) => f.startsWith(blob[1] + '.'));
    if (hit) { s.writeHead(200, { 'content-type': MIME[path.extname(hit)] }); return s.end(fs.readFileSync(path.join(realDir, hit))); }
    s.writeHead(404); return s.end('');
  }
  const file = path.join(projectDir, u.replace(/^\/+/, ''));
  if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) { s.writeHead(404); return s.end(''); }
  let body = fs.readFileSync(file);
  const stem = path.basename(file).replace(/\.dc\.html$/, '');
  if (file.endsWith('.dc.html') && !shot.has(stem)) {
    // The marker is what "an edit to this file" looks like at the page.
    body = body.toString('utf8').replace('</helmet>', `</helmet>\n<i data-probe="${stem}" hidden="hidden"></i>`);
  }
  s.writeHead(200, { 'content-type': MIME[path.extname(file)] || 'application/octet-stream' });
  s.end(body);
});
(async () => {
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  const port = server.address().port;
  const browser = await chromium.launch();
  const out = {};
  let i = 0;
  async function worker() {
    while (i < screens.length) {
      const board = screens[i++];
      const w = /^Desktop/.test(board) ? 1440 : 360;
      const ctx = await browser.newContext({ viewport: { width: w, height: w === 360 ? 800 : 900 }, reducedMotion: 'reduce' });
      const page = await ctx.newPage();
      const errors = [];
      page.on('pageerror', (e) => errors.push(String(e.message).slice(0, 160)));
      await page.goto(`http://127.0.0.1:${port}/${board}.dc.html`, { waitUntil: 'load', timeout: 60000 });
      await page.waitForTimeout(3000);
      out[board] = await page.evaluate(() => {
        const vis = (el) => { const s = getComputedStyle(el); if (s.display === 'none' || s.visibility === 'hidden') return false; const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
        const owner = (el) => { const h = el.closest('[data-sc-name]'); return h ? h.getAttribute('data-sc-name') : '(root)'; };
        const hosts = {}; document.querySelectorAll('[data-sc-name]').forEach((h) => { const n = h.getAttribute('data-sc-name'); hosts[n] = (hosts[n] || 0) + 1; });
        const probes = {}; document.querySelectorAll('[data-probe]').forEach((p) => { const n = p.getAttribute('data-probe'); probes[n] = (probes[n] || 0) + 1; });
        const tally = (sel, f) => { const m = {}; document.querySelectorAll(sel).forEach((e) => { if (!vis(e) || (f && !f(e))) return; const o = owner(e); m[o] = (m[o] || 0) + 1; }); return m; };
        const textRoot = {}; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n; let rootText = 0, compText = 0;
        while ((n = w.nextNode())) { const t = n.nodeValue.trim(); if (!t) continue; const e = n.parentElement; if (!e || ['SCRIPT', 'STYLE', 'TITLE'].includes(e.tagName) || !vis(e)) continue; if (owner(e) === '(root)' || e.closest('[data-sc-name]') === document.querySelector('[data-sc-name]')) rootText++; else compText++; }
        const rootHost = document.querySelector('[data-sc-name]');
        return {
          rootName: rootHost && rootHost.getAttribute('data-sc-name'),
          hosts, probes, rootText, compText,
          svg: tally('svg'), button: tally('button'), input: tally('input'), heading: tally('h1,h2,h3,h4'),
          harga: tally('[data-harga]'), img: tally('img'), link: tally('a'),
        };
      });
      out[board].errors = errors;
      await ctx.close();
    }
  }
  await Promise.all(Array.from({ length: 6 }, worker));
  fs.writeFileSync(outFile, JSON.stringify(out));
  await browser.close();
  server.close();
})();
