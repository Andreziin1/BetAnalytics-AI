// Fixtures sintéticas: não representam partidas reais.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import {build} from 'esbuild';
import {readFile, mkdtemp, rm} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';

const fixture = JSON.parse(await readFile(new URL('./analysis.fixture.json', import.meta.url)));
test('interface: busca, análise parcial, históricos, vazio, erro e cancelamento', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'bet-ui-'));
  const dom = new JSDOM('<div id="root"></div>', {url:'http://localhost', pretendToBeVisual:true, runScripts:'outside-only'});
  try {
    await build({entryPoints:['src/main.jsx'], bundle:true, outfile:join(dir,'app.js'), format:'iife', loader:{'.css':'empty'}, define:{'import.meta.env':'{}','process.env.NODE_ENV':'"production"'}});
    let mode='success'; const requests=[];
    dom.window.fetch = async (url, {signal}) => {
      requests.push(url);
      if (url.includes('/competitions')) return {ok:true,json:async()=>({competitions:[{code:'PL', name:'Premier League'},{code:'BSA',name:'Brasileirão Série A'}]})};
      if (url.includes('/analysis')) {
        if(mode==='pending') return new Promise((resolve,reject)=>signal.addEventListener('abort',()=>reject(new dom.window.DOMException('cancelado','AbortError'))));
        if(mode==='error') return {ok:false,status:429,headers:{get:()=> '30'},json:async()=>({error:{message:'Limite atingido'}})};
        return {ok:true,json:async()=>fixture};
      }
      return {ok:true,json:async()=>({matches:mode==='empty' ? [] : [{id:999,date:'2026-10-09T12:00:00Z',competition:{name:'Liga'},home_team:{name:'Time 1'},away_team:{name:'Time 2'}}]})};
    };
    dom.window.AbortController = AbortController;
    dom.window.eval(await readFile(join(dir,'app.js'),'utf8'));
    const document = dom.window.document;
    const waitFor = async (fn) => {for(let i=0;i<100;i++){if(fn())return;await new Promise(r=>setTimeout(r,10));}assert.fail('Estado esperado não apareceu');};
    const click = (text) => {const el=[...document.querySelectorAll('button')].find(e=>e.textContent===text && !e.closest('[hidden]'));assert.ok(el,text);el.click();};
    await waitFor(()=>document.querySelector('select option')?.textContent==='Premier League');
    click('Buscar jogos'); await waitFor(()=>document.querySelector('.analysis-button'));
    assert.ok(requests.some(url=>url.includes('competitions=PL')));
    document.querySelector('.league-item[aria-pressed="false"]').click();
    await waitFor(()=>requests.some(url=>url.includes('competitions=BSA')) && document.querySelector('.result-heading h2')?.textContent==='Brasileirão Série A');
    assert.equal(document.querySelector('.result-heading h2').textContent,'Brasileirão Série A');
    click('Ver análise'); await waitFor(()=>document.querySelector('.comparison'));
    assert.match(document.body.textContent,/Limitações dos dados/);
    assert.equal(document.querySelectorAll('.team-analysis').length,3);
    assert.ok(document.querySelector('.results').closest('[hidden]'),'A lista deve ficar oculta na análise');
    assert.match(document.body.textContent,/1 de 10 jogos/);
    assert.match(document.body.textContent,/Ambas marcam/);
    assert.match(document.body.textContent,/1 de 1 jogos \(100%\)/);
    assert.match(document.body.textContent,/Jogos sem sofrer gols/);
    assert.match(document.body.textContent,/0 de 1 jogos \(0%\)/);
    assert.match(document.body.textContent,/Média de gols totais por jogo/);
    click('Últimos jogos'); await waitFor(()=>document.querySelector('table'));
    assert.match(document.body.textContent,/2 × 1/);
    click('Confrontos diretos'); await waitFor(()=>document.querySelector('.h2h-stats'));
    click('Origem dos dados'); await waitFor(()=>document.querySelector('.provenance'));
    assert.match(document.body.textContent,/Corte:/);
    click('Voltar às partidas'); await waitFor(()=>!document.querySelector('.results').closest('[hidden]'));
    assert.equal(document.activeElement.textContent,'Ver análise');
    mode='error'; click('Ver análise'); await waitFor(()=>document.querySelector('[role="alert"]'));
    assert.match(document.body.textContent,/30 segundos/);
    mode='pending'; click('Tentar novamente'); await waitFor(()=>document.querySelector('[aria-busy="true"]'));
    click('Cancelar'); await waitFor(()=>!document.querySelector('[aria-busy="true"]'));
    assert.doesNotMatch(document.body.textContent,/Limite atingido/);
    mode='empty'; click('Buscar jogos'); await waitFor(()=>document.body.textContent.includes('Nenhuma partida futura encontrada.'));
    assert.equal(document.querySelectorAll('.match-card').length,0);
  } finally {dom.window.close();await rm(dir,{recursive:true,force:true});}
});
