import {chromium} from 'playwright';import {execFileSync} from 'child_process';
const b=await chromium.launch();const norm=s=>s.replace(/\s+/g,' ').trim();
for (const [w,dpr] of [[390,1],[1440,2]]){
  const p=await b.newPage({viewport:{width:w,height:900},deviceScaleFactor:dpr});
  await p.goto('http://127.0.0.1:8941/type/specimen.html');await p.evaluate(()=>document.fonts.ready);
  for (const o of ['P0','T1','T2','T3']){
    const els=p.locator(`[data-opt=${o}] .hd, [data-opt=${o}] .labels span, [data-opt=${o}] .small span`);
    for(let i=0;i<await els.count();i++){const el=els.nth(i);const t=norm(await el.innerText());await el.screenshot({path:'el.png'});
      const r=norm(execFileSync('tesseract',['el.png','-','--psm','6'],{stdio:['ignore','pipe','ignore']}).toString());
      if(r!==t) console.log(`${w}@${dpr} ${o}: "${t}" -> "${r}"`);}
  }
  await p.close();
}
await b.close();
