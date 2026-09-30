import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
const require = createRequire(execSync('npm root -g').toString().trim() + '/');
const { chromium } = require('playwright');
const root = path.resolve('missions/website-redesign-3/slices/02-references-and-comps/proof/comps');
const requests = [];
const server = http.createServer((req,res) => {
 const pathname = decodeURIComponent(new URL(req.url,'http://localhost').pathname);
 const file = path.resolve(root,'.'+pathname+(pathname.endsWith('/')?'index.html':''));
 if (!file.startsWith(root+path.sep)) {res.writeHead(403).end(); return;}
 try {const data=fs.readFileSync(file); requests.push({url:req.url,length:data.length});
 const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.woff2':'font/woff2'};
 res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream','Content-Length':data.length});res.end(data);
 } catch(e) {res.writeHead(404).end();}
});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const alternate=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch();
try {
 for (const [base,mode] of [['http://127.0.0.1:8941','granted'],['http://127.0.0.1:8941','denied'],[alternate,'granted'],[alternate,'denied']]) {
 const context=await browser.newContext({viewport:{width:390,height:844}});
 const page=await context.newPage();
 await page.addInitScript(mode => Object.defineProperty(navigator,'clipboard',{value:{writeText:t=>mode==='granted'?(window.__copied=t,Promise.resolve()):Promise.reject(new DOMException('denied','NotAllowedError'))}}),mode);
 const failed=[],scripts=[];
 page.on('requestfailed',r=>failed.push({url:r.url(),failure:r.failure(),headers:r.headers()}));
 page.on('response',r=>{if(r.url().includes('/kit/')&&r.url().endsWith('.js'))scripts.push({url:r.url(),status:r.status()});});
 await page.goto(`${base}/page-b/?static`,{waitUntil:'networkidle',timeout:30000});
 const clientFetch=await page.evaluate(async()=>{try {const r=await fetch('../kit/sections.js');return {status:r.status,bytes:(await r.text()).length};}catch(e){return {error:String(e)};}});
 console.log(JSON.stringify({base,failed,scripts,clientFetch,state:await page.evaluate(()=>({copy:!document.querySelector('#copy').hidden,motion:typeof Zm}))}));
 await context.close();
 }
 console.log(JSON.stringify({alternateServerRequests:requests}));
} finally {await browser.close();await new Promise(r=>server.close(r));}
