// States audit. Proves focus, hover, layout, disabled and touch behaviour with a real browser, on every screen
// at its real size, in the default state.
// Usage: DC_RUNTIME=... REAL_IMAGES=... node states_audit.cjs <projectDir> <screensJson> <outJson> [--only=Board,Board]
const http = require('http');
const fs = require('fs');
const path = require('path');
const { createRequire } = require('module');
const { execSync } = require('child_process');
const groot = execSync('npm root -g').toString().trim();
const req = createRequire(path.join(groot, '@playwright/cli/package.json'));
const { chromium } = req('playwright');
const [projectDir, screensFile, outFile, ...rest] = process.argv.slice(2);
const onlyArg = rest.find((a) => a.startsWith('--only='));
let screens = JSON.parse(fs.readFileSync(screensFile, 'utf8'));
if (onlyArg) screens = onlyArg.slice(7).split(',');
const SCRATCH = path.resolve(__dirname, '..');
const canvas = JSON.parse(fs.readFileSync(path.join(SCRATCH, 'live-check/project/canvas.json'), 'utf8'));
const realDir = process.env.REAL_IMAGES;
const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml', '.gif': 'image/gif' };
const server = http.createServer((q, s) => {
  const u = decodeURIComponent(q.url.split('?')[0]);
  if (u.endsWith('/support.js')) { s.writeHead(200, { 'content-type': MIME['.js'] }); return s.end(fs.readFileSync(process.env.DC_RUNTIME)); }
  const blob = u.match(/\/_blob\/([0-9a-f]+)/);
  if (blob) {
    const hit = fs.readdirSync(realDir).find((f) => f.startsWith(blob[1] + '.'));
    if (hit) { s.writeHead(200, { 'content-type': MIME[path.extname(hit)] || 'application/octet-stream' }); return s.end(fs.readFileSync(path.join(realDir, hit))); }
    s.writeHead(404); return s.end('');
  }
  const file = path.join(projectDir, u.replace(/^\/+/, ''));
  if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) { s.writeHead(404); return s.end(''); }
  s.writeHead(200, { 'content-type': MIME[path.extname(file)] || 'application/octet-stream' });
  s.end(fs.readFileSync(file));
});

// Runs in the page: helpers shared by every check.
const HELPERS = () => {
  const vis = (el) => { const s = getComputedStyle(el); if (s.display === 'none' || s.visibility === 'hidden') return false; const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const owner = (el) => { const h = el.closest('[data-sc-name]'); return h ? h.getAttribute('data-sc-name') : '(root)'; };
  const label = (el) => ({ owner: owner(el), tag: el.tagName.toLowerCase(), kontrol: el.getAttribute('data-kontrol') || '', teks: (el.getAttribute('aria-label') || el.textContent || el.getAttribute('placeholder') || '').trim().slice(0, 40) });
  const PROPS = ['backgroundColor', 'backgroundImage', 'color', 'boxShadow', 'textDecorationLine', 'textDecorationColor', 'textDecorationThickness', 'filter', 'transform', 'borderTopColor', 'borderRightColor', 'borderBottomColor', 'borderLeftColor', 'opacity'];
  const snap = (el) => {
    const nodes = [el, ...Array.from(el.querySelectorAll('*')).slice(0, 80)];
    return nodes.map((n) => { const s = getComputedStyle(n); const o = {}; PROPS.forEach((p) => { o[p] = s[p]; }); return o; });
  };
  const rects = (el) => { const base = el.getBoundingClientRect(); const nodes = Array.from(el.querySelectorAll('*')).slice(0, 80); return { w: base.width, h: base.height, kids: nodes.map((n) => { const r = n.getBoundingClientRect(); return [Math.round((r.left - base.left) * 2) / 2, Math.round((r.top - base.top) * 2) / 2, Math.round(r.width * 2) / 2, Math.round(r.height * 2) / 2]; }), page: document.documentElement.scrollHeight }; };
  const diff = (a, b) => { const out = []; for (let i = 0; i < Math.min(a.length, b.length); i++) { for (const p of PROPS) if (a[i][p] !== b[i][p]) out.push(p + (i === 0 ? '' : '@child')); } return Array.from(new Set(out)); };
  const pointOn = (el) => {
    const inRect = (r) => { const pts = [[.5, .5], [.2, .5], [.8, .5], [.5, .2], [.5, .8], [.1, .1], [.9, .9], [.9, .1], [.1, .9]]; for (const [fx, fy] of pts) { const x = r.left + r.width * fx; const y = r.top + r.height * fy; if (x < 0 || y < 0 || x >= innerWidth || y >= innerHeight) continue; const t = document.elementFromPoint(x, y); if (t && (t === el || el.contains(t))) return { x, y }; } return null; };
    for (const r of el.getClientRects()) { const p = inRect(r); if (p) return p; }
    return null;
  };
  const clipped = (el) => {
    const s = getComputedStyle(el); const off = parseFloat(s.outlineOffset) || 0; const w = parseFloat(s.outlineWidth) || 0; const out = Math.max(0, off + w);
    const r = el.getBoundingClientRect(); const R = { l: r.left - out, t: r.top - out, r: r.right + out, b: r.bottom + out }; const by = [];
    for (let p = el.parentElement; p; p = p.parentElement) {
      const c = getComputedStyle(p);
      if (c.display === 'contents') continue;
      if (c.overflowX !== 'visible' || c.overflowY !== 'visible' || c.clipPath !== 'none') {
        const q = p.getBoundingClientRect(); const left = q.left + p.clientLeft; const top = q.top + p.clientTop; const right = left + p.clientWidth; const bottom = top + p.clientHeight;
        if (R.l < left - .6 || R.t < top - .6 || R.r > right + .6 || R.b > bottom + .6) by.push(owner(p) + ':' + (p.getAttribute('data-sc-name') ? 'host' : p.tagName.toLowerCase()) + ':' + c.overflowX + '/' + c.overflowY);
      }
      if (c.position === 'fixed') break;
    }
    if (R.l < -.6 || R.r > innerWidth + .6) by.push('viewport-x');
    return by;
  };
  window.__sa = { vis, owner, label, snap, rects, diff, pointOn, clipped };
};

async function ringVisible(page, helper, el, offset) {
  // Screenshot before and after focus; for lines crossing each side of the element, the ring is seen when some
  // pixel out to the ring's outer edge differs from what was there by at least 3:1.
  const box = await el.evaluate((n) => { n.scrollIntoView({ block: 'center', inline: 'center' }); const r = n.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; });
  if (box.w < 1 || box.h < 1) return null;
  const pad = 8; const clip = { x: Math.max(0, box.x - pad), y: Math.max(0, box.y - pad), width: box.w + pad * 2, height: box.h + pad * 2 };
  const vp = page.viewportSize();
  clip.width = Math.min(clip.width, vp.width - clip.x); clip.height = Math.min(clip.height, vp.height - clip.y);
  if (clip.width < 4 || clip.height < 4) return null;
  await el.evaluate((n) => n.blur());
  const before = (await page.screenshot({ clip, animations: 'disabled' })).toString('base64');
  await el.evaluate((n) => n.focus({ preventScroll: true }));
  const after = (await page.screenshot({ clip, animations: 'disabled' })).toString('base64');
  await el.evaluate((n) => n.blur());
  const b = { x: box.x - clip.x, y: box.y - clip.y, w: box.w, h: box.h };
  return helper.evaluate(async ({ before, after, b, offset }) => {
    const load = async (d) => { const i = new Image(); i.src = 'data:image/png;base64,' + d; await i.decode(); const c = document.createElement('canvas'); c.width = i.naturalWidth; c.height = i.naturalHeight; const x = c.getContext('2d'); x.drawImage(i, 0, 0); return x.getImageData(0, 0, c.width, c.height); };
    const A = await load(before); const B = await load(after);
    const lum = (d, x, y) => { x = Math.round(x); y = Math.round(y); if (x < 0 || y < 0 || x >= d.width || y >= d.height) return null; const i = (y * d.width + x) * 4; const f = (v) => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(d.data[i]) + .7152 * f(d.data[i + 1]) + .0722 * f(d.data[i + 2]); };
    const best = (x, y, dx, dy, from, to) => { let m = 0; for (let k = from; k <= to; k += .5) { const p = lum(A, x + dx * k, y + dy * k); const q = lum(B, x + dx * k, y + dy * k); if (p === null || q === null) continue; const r = (Math.max(p, q) + .05) / (Math.min(p, q) + .05); if (r > m) m = r; } return m; };
    const lines = []; const from = offset < 0 ? -4 : 0; const to = offset < 0 ? 0 : 5;
    for (const t of [.25, .4, .5, .6, .75]) { lines.push(['top', best(b.x + b.w * t, b.y, 0, -1, from, to)], ['bottom', best(b.x + b.w * t, b.y + b.h, 0, 1, from, to)], ['left', best(b.x, b.y + b.h * t, -1, 0, from, to)], ['right', best(b.x + b.w, b.y + b.h * t, 1, 0, from, to)]); }
    const seen = lines.filter((l) => l[1] >= 3).length / lines.length;
    const sides = {}; lines.forEach(([s, v]) => { sides[s] = Math.max(sides[s] || 0, v); });
    return { frac: Math.round(seen * 100) / 100, sides };
  }, { before, after, b, offset });
}

async function auditScreen(browser, helper, board) {
  const entry = canvas.boards[board + '.dc.html'] || {};
  const w = Number(entry.w) || (/^Desktop/.test(board) ? 1440 : 360); const h = Number(entry.h) || (w === 360 ? 800 : 900);
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, reducedMotion: 'reduce' });
  const page = await ctx.newPage();
  const res = { w, h, errors: [], uncovered: [], focus: { total: 0, missing: [], offsets: {}, clipped: [], ringWeak: [], ringChecked: 0 }, hover: { total: 0, noChange: [], covered: [], pointerNone: [], layout: [], direct: 0, real: 0 }, disabled: { total: 0, changed: [] } };
  page.on('pageerror', (e) => res.errors.push(String(e.message).slice(0, 160)));
  await page.goto(`http://127.0.0.1:${server.address().port}/${board}.dc.html`, { waitUntil: 'load', timeout: 60000 });
  await page.waitForTimeout(Number(process.env.SETTLE_MS || 2500));
  await page.evaluate(HELPERS);

  // Coverage: every rendered control carries a kind.
  res.uncovered = await page.evaluate(() => Array.from(document.querySelectorAll('a,button,input,textarea,select,summary,[role=button],[tabindex]')).filter((e) => !e.hasAttribute('data-kontrol') && e.getAttribute('tabindex') !== '-1').map((e) => __sa.label(e)));

  // Focus: Tab once so the page is in keyboard modality, then focus every visible focusable element.
  await page.keyboard.press('Tab');
  const focusSel = 'a[href],button:not([disabled]),input:not([disabled]),textarea:not([disabled]),select:not([disabled]),summary,[tabindex]:not([tabindex="-1"]),[role=button]';
  const fres = await page.evaluate((sel) => {
    const out = { total: 0, missing: [], offsets: {}, clipped: [] };
    document.querySelectorAll(sel).forEach((el) => {
      if (!__sa.vis(el)) return;
      out.total++;
      el.focus();
      const s = getComputedStyle(el);
      const ok = document.activeElement === el && el.matches(':focus-visible') && s.outlineStyle !== 'none' && s.outlineWidth === '2px';
      if (!ok) out.missing.push({ ...__sa.label(el), active: document.activeElement === el, fv: el.matches(':focus-visible'), style: s.outlineStyle, width: s.outlineWidth });
      out.offsets[s.outlineOffset] = (out.offsets[s.outlineOffset] || 0) + 1;
      const by = __sa.clipped(el);
      if (by.length) out.clipped.push({ ...__sa.label(el), by: by.slice(0, 2) });
      el.blur();
    });
    return out;
  }, focusSel);
  Object.assign(res.focus, fres, { ringWeak: [], ringChecked: 0 });
  await page.waitForTimeout(150);

  // Ring seen with real pixels: one element per component and kind on each screen.
  const seen = new Set();
  const handles = await page.$$(focusSel);
  for (const el of handles) {
    const info = await el.evaluate((n) => (__sa.vis(n) ? { ...__sa.label(n), off: parseFloat(getComputedStyle(n).outlineOffset) || 0 } : null)).catch(() => null);
    if (!info) continue;
    const key = info.owner + '|' + info.kontrol;
    if (seen.has(key)) continue;
    seen.add(key);
    await el.evaluate((n) => n.focus({ preventScroll: true })).catch(() => {});
    const off = await el.evaluate((n) => parseFloat(getComputedStyle(n).outlineOffset) || 0).catch(() => 0);
    await el.evaluate((n) => n.blur()).catch(() => {});
    const r = await ringVisible(page, helper, el, off).catch(() => null);
    if (!r) continue;
    res.focus.ringChecked++;
    if (r.frac < 0.5) res.focus.ringWeak.push({ ...info, frac: r.frac, sides: r.sides });
  }

  // Hover: real mouse on every visible enabled link and button.
  const parked = async () => { await page.mouse.move(0, 0); };
  await parked();
  const hovers = await page.$$('a[href],button:not([disabled])');
  for (const el of hovers) {
    const info = await el.evaluate((n) => (__sa.vis(n) ? __sa.label(n) : null)).catch(() => null);
    if (!info) continue;
    res.hover.total++;
    await el.evaluate((n) => n.scrollIntoView({ block: 'center', inline: 'center' })).catch(() => {});
    await parked();
    const before = await el.evaluate((n) => ({ s: __sa.snap(n), r: __sa.rects(n), pe: getComputedStyle(n).pointerEvents, hov: n.matches(':hover') }));
    const pt = await el.evaluate((n) => __sa.pointOn(n));
    let after; let how;
    if (pt) {
      await page.mouse.move(pt.x, pt.y);
      after = await el.evaluate((n) => ({ s: __sa.snap(n), r: __sa.rects(n), hov: n.matches(':hover') }));
      how = after.hov ? 'real' : 'miss';
    }
    if (!pt || how === 'miss') {
      // Covered, or pointer-events: none: prove the shared rule through the preview attribute instead.
      const none = before.pe === 'none';
      after = await el.evaluate((n) => { const had = n.getAttribute('data-keadaan'); n.setAttribute('data-keadaan', 'hover'); const v = { s: __sa.snap(n), r: __sa.rects(n) }; if (had === null) n.removeAttribute('data-keadaan'); else n.setAttribute('data-keadaan', had); return v; });
      how = 'direct';
      res.hover.direct++;
      (none ? res.hover.pointerNone : res.hover.covered).push(info);
    } else { res.hover.real++; }
    const changed = await page.evaluate(([a, b]) => __sa.diff(a, b), [before.s, after.s]);
    if (!changed.length) res.hover.noChange.push({ ...info, how });
    const moved = before.r.w !== after.r.w || before.r.h !== after.r.h || before.r.page !== after.r.page || JSON.stringify(before.r.kids) !== JSON.stringify(after.r.kids);
    if (moved) res.hover.layout.push({ ...info, w: [before.r.w, after.r.w], h: [before.r.h, after.r.h], page: [before.r.page, after.r.page], kids: JSON.stringify(before.r.kids) !== JSON.stringify(after.r.kids) });
    await parked();
  }

  // Disabled: no reaction to the pointer.
  const dis = await page.$$('button:disabled,input:disabled,[aria-disabled="true"]');
  for (const el of dis) {
    const info = await el.evaluate((n) => (__sa.vis(n) ? __sa.label(n) : null)).catch(() => null);
    if (!info) continue;
    res.disabled.total++;
    await el.evaluate((n) => n.scrollIntoView({ block: 'center', inline: 'center' }));
    await parked();
    const a = await el.evaluate((n) => __sa.snap(n));
    const box = await el.boundingBox();
    if (box) await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
    const b = await el.evaluate((n) => __sa.snap(n));
    const changed = await page.evaluate(([x, y]) => __sa.diff(x, y), [a, b]);
    if (changed.length) res.disabled.changed.push({ ...info, changed });
    await parked();
  }
  await ctx.close();
  return res;
}

async function touchScreen(browser, board) {
  const ctx = await browser.newContext({ viewport: { width: 360, height: 800 }, hasTouch: true, isMobile: true, reducedMotion: 'reduce' });
  const page = await ctx.newPage();
  await page.goto(`http://127.0.0.1:${server.address().port}/${board}.dc.html`, { waitUntil: 'load', timeout: 60000 });
  await page.waitForTimeout(1500);
  const media = await page.evaluate(() => ({ hover: matchMedia('(hover: hover)').matches, coarse: matchMedia('(pointer: coarse)').matches }));
  const out = { board, media, tapped: 0, stuck: [] };
  const SNAP = (n) => { const s = getComputedStyle(n); return { bg: s.backgroundColor, color: s.color, filter: s.filter, shadow: s.boxShadow, deco: s.textDecorationLine, border: s.borderBottomColor, hov: n.matches(':hover') }; };
  const els = await page.$$('button:not([disabled])[data-kontrol],a[href^="#"][data-kontrol]');
  const seen = new Set();
  for (const el of els) {
    const k = await el.evaluate((n) => (n.getBoundingClientRect().width > 0 ? n.getAttribute('data-kontrol') : null)).catch(() => null);
    if (!k || seen.has(k)) continue;
    seen.add(k);
    const before = await el.evaluate(SNAP).catch(() => null);
    if (!before) continue;
    const ok = await el.tap({ timeout: 1500, force: true }).then(() => true).catch(() => false);
    if (!ok) continue;
    await page.waitForTimeout(250);
    const after = await el.evaluate(SNAP).catch(() => null);
    if (!after) continue;
    out.tapped++;
    // After the finger lifts, the rendered colours must not be the hover colours. A control may legitimately
    // change state on tap (selected); the preview attribute says what its hover colours would have been.
    const hoverLook = await el.evaluate((n, SNAPS) => { const had = n.getAttribute('data-keadaan'); n.setAttribute('data-keadaan', 'hover'); const s = getComputedStyle(n); const v = { bg: s.backgroundColor, color: s.color, filter: s.filter, shadow: s.boxShadow, deco: s.textDecorationLine, border: s.borderBottomColor }; if (had === null) n.removeAttribute('data-keadaan'); else n.setAttribute('data-keadaan', had); return v; }).catch(() => null);
    const isHover = hoverLook && ['bg', 'color', 'filter', 'shadow', 'deco', 'border'].some((p) => hoverLook[p] !== before[p] && hoverLook[p] === after[p]);
    if (isHover) out.stuck.push({ kontrol: k, before, after, hoverLook });
    await page.evaluate(() => { if (document.activeElement) document.activeElement.blur(); });
  }
  await ctx.close();
  return out;
}

async function motion(browser, board) {
  const out = {};
  for (const pref of ['no-preference', 'reduce']) {
    const ctx = await browser.newContext({ viewport: { width: 360, height: 800 }, reducedMotion: pref });
    const page = await ctx.newPage();
    await page.goto(`http://127.0.0.1:${server.address().port}/${board}.dc.html`, { waitUntil: 'load', timeout: 60000 });
    await page.waitForTimeout(1500);
    out[pref] = await page.evaluate(() => { const m = {}; document.querySelectorAll('[data-kontrol]').forEach((e) => { if (e.matches('[data-grid],[data-grid-tile],[data-kat-set] a')) return; const s = getComputedStyle(e); const k = s.transitionDuration.split(',')[0].trim(); m[k] = (m[k] || 0) + 1; }); return m; });
    await ctx.close();
  }
  return out;
}

function staticCoverage() {
  // Every interactive tag in every non-sheet component template.
  const bad = [];
  for (const f of fs.readdirSync(projectDir)) {
    if (!f.endsWith('.dc.html') || f.startsWith('Sheet')) continue;
    const s = fs.readFileSync(path.join(projectDir, f), 'utf8').split('</x-dc>')[0];
    for (const m of s.matchAll(/<(a|button|input|select|textarea|summary)\b[^>]*>/g)) if (!/data-kontrol=/.test(m[0])) bad.push({ file: f, tag: m[1], src: m[0].slice(0, 90) });
    for (const m of s.matchAll(/<(div|span|li|p)\b[^>]*(tabindex|role="button")[^>]*>/gi)) if (!/data-kontrol=/.test(m[0])) bad.push({ file: f, tag: m[1], src: m[0].slice(0, 90) });
  }
  return bad;
}

(async () => {
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  const browser = await chromium.launch();
  const hctx = await browser.newContext();
  const out = { screens: {}, touch: [], static: staticCoverage() };
  let i = 0;
  async function worker() {
    const helper = await hctx.newPage();
    while (i < screens.length) {
      const board = screens[i++];
      try { out.screens[board] = await auditScreen(browser, helper, board); } catch (e) { out.screens[board] = { fatal: String(e).slice(0, 300) }; }
      process.stderr.write(board + ' ');
    }
    await helper.close();
  }
  await Promise.all(Array.from({ length: Number(process.env.WORKERS || 6) }, worker));
  const touchBoards = screens.filter((s) => !/^Desktop/.test(s));
  for (const b of touchBoards) out.touch.push(await touchScreen(browser, b).catch((e) => ({ board: b, fatal: String(e).slice(0, 200) })));
  if (touchBoards[0]) out.motion = await motion(browser, touchBoards[0]);
  await browser.close();
  server.close();
  // Totals
  const T = { screens: 0, uncovered: 0, focusTotal: 0, focusMissing: 0, clipped: 0, ringChecked: 0, ringWeak: 0, hoverTotal: 0, hoverReal: 0, hoverDirect: 0, noChange: 0, covered: 0, pointerNone: 0, layout: 0, disabledTotal: 0, disabledChanged: 0, errors: 0, fatal: 0, offsets: {} };
  for (const r of Object.values(out.screens)) {
    if (r.fatal) { T.fatal++; continue; }
    T.screens++; T.uncovered += r.uncovered.length; T.focusTotal += r.focus.total; T.focusMissing += r.focus.missing.length; T.clipped += r.focus.clipped.length; T.ringChecked += r.focus.ringChecked; T.ringWeak += r.focus.ringWeak.length;
    T.hoverTotal += r.hover.total; T.hoverReal += r.hover.real; T.hoverDirect += r.hover.direct; T.noChange += r.hover.noChange.length; T.covered += r.hover.covered.length; T.pointerNone += r.hover.pointerNone.length; T.layout += r.hover.layout.length; T.disabledTotal += r.disabled.total; T.disabledChanged += r.disabled.changed.length; T.errors += r.errors.length;
    for (const [k, v] of Object.entries(r.focus.offsets)) T.offsets[k] = (T.offsets[k] || 0) + v;
  }
  T.staticUncovered = out.static.length;
  T.touchBoards = out.touch.length; T.touchTapped = out.touch.reduce((a, t) => a + (t.tapped || 0), 0); T.touchStuck = out.touch.reduce((a, t) => a + (t.stuck ? t.stuck.length : 0), 0); T.touchHoverMedia = out.touch.filter((t) => t.media && t.media.hover).length; T.touchFatal = out.touch.filter((t) => t.fatal).length;
  out.totals = T;
  fs.writeFileSync(outFile, JSON.stringify(out, null, 1));
  console.log(JSON.stringify(T));
  console.log('motion', JSON.stringify(out.motion));
})();
