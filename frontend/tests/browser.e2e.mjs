// Teste em navegador real com respostas sintéticas explícitas. Não usa API_KEY.
import {test} from 'node:test';
import {spawn} from 'node:child_process';
import assert from 'node:assert/strict';
import {readFile, mkdir} from 'node:fs/promises';
import {chromium} from 'playwright';
const fixture=JSON.parse(await readFile(new URL('./analysis.fixture.json',import.meta.url)));
const url=process.env.E2E_BASE_URL || 'http://127.0.0.1:5179';
const server=process.env.E2E_BASE_URL ? null : spawn(process.execPath,['node_modules/vite/bin/vite.js','--host','127.0.0.1','--port','5179','--strictPort'],{stdio:'ignore'});
if(server){
  let ready=false;
  for(let i=0;i<100;i++){try{if((await fetch(url)).ok){ready=true;break;}}catch{}await new Promise(r=>setTimeout(r,100));}
  if(!ready){server.kill();throw new Error('Vite não iniciou na porta 5179.');}
}

let browser;
try { browser=await chromium.launch({headless:true,executablePath:process.env.PLAYWRIGHT_EXECUTABLE_PATH || undefined,args:['--no-sandbox','--disable-dev-shm-usage']}); }
catch(error){server?.kill();throw error;}
try {
  for(const viewport of [{width:1440,height:1000},{width:390,height:844}]) {
    await test(`fluxos e layout ${viewport.width}px`,async()=>{
      const page=await browser.newPage({viewport});const errors=[];page.on('pageerror',e=>errors.push(e.message));
      let mode='success', releasePending;
      await page.route('**/api/**',async route=>{
        const path=new URL(route.request().url()).pathname;
        if(path.endsWith('/competitions'))return route.fulfill({json:{competitions:[{code:'PL',name:'Premier League'}]}});
        if(path.endsWith('/analysis')){
          if(mode==='error')return route.fulfill({status:429,headers:{'Retry-After':'30'},json:{error:{message:'Limite atingido'}}});
          if(mode==='pending'){await new Promise(resolve=>{releasePending=resolve;});return route.fulfill({json:fixture}).catch(()=>{});}
          return route.fulfill({json:fixture});
        }
        return route.fulfill({json:{matches:mode==='empty'?[]:[
          {id:999,date:'2026-10-25T01:00:00Z',competition:{name:'Liga de teste'},home_team:{name:'São Paulo',crest:'https://invalid.example/crest.png'},away_team:{name:'Time 2'}},
          {id:1000,date:'2026-10-26T18:00:00Z',competition:{name:'Liga de teste'},home_team:{name:'Time 3'},away_team:{name:'Time 4'}},
        ]}});
      });
      await page.route('https://invalid.example/**',r=>r.abort());
      await page.goto(url);await page.getByRole('button',{name:'Buscar jogos',exact:true}).click();
      await page.locator('.match-card').first().waitFor();
      assert.equal(await page.locator('.match-card').count(),2);
      await page.getByLabel('Buscar time').fill('sao paulo');assert.equal(await page.locator('.match-card').count(),1);
      await page.getByLabel('Data em Brasília').fill('2026-10-24');assert.equal(await page.locator('.match-card').count(),1);
      await page.getByLabel('Data em Brasília').fill('2026-10-25');await page.getByText('Nenhum jogo corresponde aos filtros.',{exact:false}).waitFor();
      await page.getByRole('button',{name:'Limpar filtros'}).click();
      await page.getByLabel('Ordenar').selectOption('desc');assert.match(await page.locator('.match-card').first().innerText(),/Time 3/);
      await page.getByRole('button',{name:'Limpar filtros'}).click();
      await page.getByRole('button',{name:'Ver análise',exact:true}).first().click();
      await page.locator('.goals-chart').waitFor();assert.equal(await page.locator('.stacked-bar').count(),2);
      await page.getByText('Desempenho em casa e fora',{exact:true}).first().click();
      await page.getByRole('button',{name:'Últimos jogos',exact:true}).click();
      assert.ok(await page.getByRole('table').first().isVisible());
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth),false,'A página não pode transbordar horizontalmente');
      if(process.env.E2E_SCREENSHOT_DIR){await mkdir(process.env.E2E_SCREENSHOT_DIR,{recursive:true});await page.screenshot({path:`${process.env.E2E_SCREENSHOT_DIR}/bet-${viewport.width}.png`,fullPage:true});}
      await page.getByRole('button',{name:'Voltar às partidas'}).click();assert.equal(await page.locator('.comparison').count(),0);
      assert.equal(await page.evaluate(()=>document.activeElement.textContent),'Ver análise');
      mode='error';await page.getByRole('button',{name:'Ver análise',exact:true}).first().click();await page.getByRole('alert').waitFor();assert.match(await page.getByRole('alert').innerText(),/30 segundos/);
      mode='pending';await page.getByRole('button',{name:'Tentar novamente',exact:true}).click();await page.getByRole('button',{name:'Cancelar',exact:true}).click();
      releasePending?.();
      await page.waitForTimeout(400);assert.equal(await page.locator('.comparison').count(),0,'Consulta cancelada não deve reaparecer');
      mode='empty';await page.getByRole('button',{name:'Buscar jogos',exact:true}).click();await page.getByText('Nenhuma partida futura encontrada.').waitFor();
      assert.deepEqual(errors,[]);await page.close();
    });
  }

} finally {await browser.close();server?.kill();}
