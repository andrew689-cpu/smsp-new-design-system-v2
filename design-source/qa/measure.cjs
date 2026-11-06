// Measure real board heights. Usage: node measure.cjs <projectDir> <listJsonFile> <outJson>
// list: [{"board":"Name","w":360}]. Output: {Name:{height,width,errors,sections:[heights]}}
const http = require('http');
const fs = require('fs');
const path = require('path');
const { createRequire } = require('module');
const { execSync } = require('child_process');
const groot = execSync('npm root -g').toString().trim();
const req = createRequire(path.join(groot, '@playwright/cli/package.json'));
const { chromium } = req('playwright');
const [projectDir, listFile, outFile] = process.argv.slice(2);
const list = JSON.parse(fs.readFileSync(listFile, 'utf8'));
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
  s.writeHead(200, { 'content-type': MIME[path.extname(file)] || 'application/octet-stream' });
  s.end(fs.readFileSync(file));
});
const NOISE = /fonts\.g|ERR_|Failed to load resource| attribute /;
(async () => {
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  const port = server.address().port;
  const browser = await chromium.launch();
  const out = {};
  const CONC = 6;
  let i = 0;
  async function worker() {
    while (i < list.length) {
      const item = list[i++];
      const ctx = await browser.newContext({ viewport: { width: item.w, height: 200 }, reducedMotion: 'reduce' });
      const page = await ctx.newPage();
      const errors = [];
      page.on('pageerror', (e) => errors.push(String(e.message).slice(0, 200)));
      page.on('console', (m) => { if (m.type() === 'error' && !NOISE.test(m.text())) errors.push(m.text().slice(0, 200)); });
      try {
        await page.goto(`http://127.0.0.1:${port}/${item.board}.dc.html`, { waitUntil: 'load', timeout: 60000 });
        await page.waitForTimeout(2200);
        const r = await page.evaluate(() => {
          const root = document.querySelector('.sc-host > div') || document.body;
          const secs = [...root.children].filter((e) => e.tagName === 'SECTION').map((e) => e.getBoundingClientRect().height);
          const content = [...document.body.querySelectorAll('*')].reduce((m, e) => { const c = getComputedStyle(e); if (c.position === 'fixed') return m; const b = e.getBoundingClientRect(); return b.height > 0 ? Math.max(m, b.bottom + window.scrollY) : m; }, 0);
          return { height: Math.ceil(content), width: document.documentElement.scrollWidth, sections: secs, logic: [...document.querySelectorAll('.sc-logic-error')].map((e) => e.textContent.slice(0, 200)) };
        });
        out[item.board] = { ...r, errors: errors.concat(r.logic) };
      } catch (e) {
        out[item.board] = { error: String(e.message).slice(0, 200), errors };
      }
      await ctx.close();
    }
  }
  await Promise.all(Array.from({ length: CONC }, worker));
  fs.writeFileSync(outFile, JSON.stringify(out));
  await browser.close();
  server.close();
})();
