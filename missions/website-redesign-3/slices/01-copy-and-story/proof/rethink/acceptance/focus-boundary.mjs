import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
const require=createRequire(execSync('npm root -g').toString().trim()+'/');
const {chromium}=require('playwright');
const browser=await chromium.launch();
try {
for(let trial=1;trial<=3;trial++) {
 const ctx=await browser.newContext({viewport:{width:1440,height:900}}),page=await ctx.newPage(),failures=[],errors=[],scripts=[];
 page.on('requestfailed',r=>failures.push({url:r.url(),failure:r.failure()}));
 page.on('pageerror',e=>errors.push(e.message));
 page.on('response',r=>{if(r.url().endsWith('.js'))scripts.push({url:r.url(),status:r.status()});});
 await page.goto('http://127.0.0.1:8941/page-b/?static');
 const want=await page.evaluate(()=>[...document.querySelectorAll('a[href],button')].filter(e=>e.getClientRects().length).map(e=>e.textContent.trim()));
 const got=[];
 for(let i=0;i<want.length+2;i++){
  await page.keyboard.press('Tab');
  const t=await page.evaluate(()=>{const a=document.activeElement;return a&&a!==document.body?(a.textContent.trim()||a.tagName):null;});
  if(t===null||got.includes(t)&&got[0]===t)break;got.push(t);
 }
 const state=await page.evaluate(()=>{const c=document.getElementById('copy');c.focus();const s=getComputedStyle(c);return {hidden:c.hidden,display:s.display,outline:s.outlineStyle+' '+s.outlineWidth,active:document.activeElement.id,focusVisible:c.matches(':focus-visible'),focus:c.matches(':focus'),motion:typeof Zm};});
 console.log(JSON.stringify({trial,want,got,state,scripts,failures,errors}));
 await ctx.close();
}
}finally{await browser.close();}
