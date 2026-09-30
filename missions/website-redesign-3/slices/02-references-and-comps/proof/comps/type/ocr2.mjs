import {chromium} from 'playwright';import {execFileSync} from 'child_process';
const b=await chromium.launch();const res={};
const norm=s=>s.toLowerCase().replace(/[’']/g,"'").replace(/[^a-z0-9.' ]/g,' ').replace(/\s+/g,' ').trim();
function lev(a,b){const d=Array.from({length:a.length+1},(_,i)=>[i]);for(let j=1;j<=b.length;j++)d[0][j]=j;for(let i=1;i<=a.length;i++)for(let j=1;j<=b.length;j++)d[i][j]=Math.min(d[i-1][j]+1,d[i][j-1]+1,d[i-1][j-1]+(a[i-1]==b[j-1]?0:1));return d[a.length][b.length];}
for (const dpr of [1,2]) for (const w of [320,390,1440,1920]){
  const p=await b.newPage({viewport:{width:w,height:900},deviceScaleFactor:dpr});
  await p.goto('http://127.0.0.1:8941/type/specimen.html');await p.evaluate(()=>document.fonts.ready);
  for (const o of ['P0','T1','T2','T3']){
    const els=p.locator(`[data-opt=${o}] .hd, [data-opt=${o}] .labels span, [data-opt=${o}] .small span`);
    const n=await els.count();let err=0,tot=0;
    for(let i=0;i<n;i++){const el=els.nth(i);const t=norm(await el.innerText());
      await el.screenshot({path:'el.png'});
      const o2=norm(execFileSync('tesseract',['el.png','-','--psm','6'],{stdio:['ignore','pipe','ignore']}).toString());
      err+=lev(t,o2);tot+=t.length;}
    (res[o]??={})[`${w}@${dpr}x`]=(1-err/tot).toFixed(3);
  }
  await p.close();
}
await b.close();console.table(res);
