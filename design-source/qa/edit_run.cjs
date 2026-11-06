
const http=require('http'),fs=require('fs'),path=require('path');
const {createRequire}=require('module');const {execSync}=require('child_process');
const req=createRequire(path.join(execSync('npm root -g').toString().trim(),'@playwright/cli/package.json'));
const {chromium}=req('playwright');
const [dir,screensFile,outFile]=process.argv.slice(2);const screens=JSON.parse(fs.readFileSync(screensFile,'utf8'));
const real=process.env.REAL_IMAGES;const M={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.svg':'image/svg+xml'};
const sv=http.createServer((q,s)=>{const u=decodeURIComponent(q.url.split('?')[0]);
 if(u.endsWith('/support.js')){s.writeHead(200,{'content-type':M['.js']});return s.end(fs.readFileSync(process.env.DC_RUNTIME));}
 const b=u.match(/\/_blob\/([0-9a-f]+)/);if(b){const h=fs.readdirSync(real).find(f=>f.startsWith(b[1]+'.'));if(h){s.writeHead(200,{'content-type':M[path.extname(h)]});return s.end(fs.readFileSync(path.join(real,h)));}s.writeHead(404);return s.end('');}
 const f=path.join(dir,u.replace(/^\/+/,''));if(!fs.existsSync(f)||fs.statSync(f).isDirectory()){s.writeHead(404);return s.end('');}
 s.writeHead(200,{'content-type':M[path.extname(f)]||'application/octet-stream'});s.end(fs.readFileSync(f));});
(async()=>{await new Promise(r=>sv.listen(0,'127.0.0.1',r));const port=sv.address().port;const br=await chromium.launch();const out={};let i=0;
async function w(){while(i<screens.length){const b=screens[i++];const W=/^Desktop/.test(b)?1440:360;const c=await br.newContext({viewport:{width:W,height:W===360?800:900},reducedMotion:'reduce'});const p=await c.newPage();
 await p.goto(`http://127.0.0.1:${port}/${b}.dc.html`,{waitUntil:'load',timeout:60000});await p.waitForTimeout(3000);
 out[b]=await p.evaluate(()=>{const vis=e=>{const s=getComputedStyle(e);const r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0;};
  const text=document.body.innerText;const own=e=>{const h=e.closest('[data-sc-name]');return h?h.getAttribute('data-sc-name'):'?';};
  const zz={};(text.match(/ZZ[A-Z]+/g)||[]).forEach(z=>zz[z]=(zz[z]||0)+1);
  const pr={};let prT=0,prE=0;document.querySelectorAll('[data-harga]').forEach(e=>{if(!vis(e)||!e.textContent.trim())return;prT++;if(getComputedStyle(e).color==='rgb(1, 2, 3)')prE++;else{const o=own(e);pr[o]=(pr[o]||0)+1;}});
  const hd={};let hT=0,hE=0;document.querySelectorAll('h1,h2,h3').forEach(e=>{if(!vis(e))return;hT++;if(getComputedStyle(e).outlineColor==='rgb(4, 5, 6)'&&getComputedStyle(e).outlineStyle==='solid')hE++;else{const o=own(e);hd[o]=(hd[o]||0)+1;}});
  let ic=0,icT=0;const ico={};document.querySelectorAll('svg').forEach(e=>{if(!vis(e))return;icT++;if(e.hasAttribute('data-edit-icon'))ic++;else{const o=own(e);ico[o]=(ico[o]||0)+1;}});
  const bt=[...document.querySelectorAll('a,button')].filter(e=>vis(e)&&getComputedStyle(e).outlineColor==='rgb(7, 8, 9)'&&getComputedStyle(e).outlineStyle==='solid').length;
  const remain=['Kalkulator Material','Bantuan dan FAQ','Kebijakan Privasi','Waspada penipuan','Konsultasi Sekarang','per batang','Lihat Selengkapnya'].filter(x=>text.toLowerCase().includes(x.toLowerCase()));
  return {zz,prT,prE,pr,hT,hE,hd,icT,ic,ico,bt,remain};});
 await c.close();}}
await Promise.all(Array.from({length:6},w));fs.writeFileSync(outFile,JSON.stringify(out));await br.close();sv.close();})();
