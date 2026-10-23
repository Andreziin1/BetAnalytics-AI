import React, {useEffect, useMemo, useState, useRef} from 'react';
import {createRoot} from 'react-dom/client';
import {api, setAccessToken} from './api';
import Analysis, {formatDate, Warnings} from './Analysis';
import './styles.css';

const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
export function brazilDate(value) {
  const parts = new Intl.DateTimeFormat('en-CA', {timeZone:'America/Sao_Paulo',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date(value));
  const get = type => parts.find(p => p.type === type).value;
  return `${get('year')}-${get('month')}-${get('day')}`;
}
function Crest({team}) {
  const [failed,setFailed] = useState(false);
  useEffect(()=>setFailed(false),[team.crest]);
  const valid = typeof team.crest === 'string' && /^https:\/\//i.test(team.crest);
  return valid && !failed ? <img src={team.crest} alt="" loading="lazy" referrerPolicy="no-referrer" onError={()=>setFailed(true)}/> : <span className="crest-fallback" aria-hidden="true">{team.name.slice(0,2).toUpperCase()}</span>;
}
function App() {
  const [analysis,setAnalysis] = useState(null);
  const [analysisError,setAnalysisError] = useState('');
  const [analysisLoading,setAnalysisLoading] = useState(false);
  const [warnings,setWarnings] = useState([]);
  const analysisRequest=useRef(null), listRequest=useRef(null), analysisRegion=useRef(null), resultRegion=useRef(null), selectedButton=useRef(null);
  const [competitions,setCompetitions]=useState([]), [competition,setCompetition]=useState('PL'), [days,setDays]=useState(7);
  const [matches,setMatches]=useState([]), [loading,setLoading]=useState(false), [error,setError]=useState('');
  const [searched,setSearched]=useState(false), [resultCompetition,setResultCompetition]=useState('PL');
  const [teamQuery,setTeamQuery]=useState(''), [dateFilter,setDateFilter]=useState(''), [sort,setSort]=useState('asc');
  const [reload,setReload]=useState(0), [needsAccess,setNeedsAccess]=useState(false), [token,setToken]=useState('');
  useEffect(()=>()=>{analysisRequest.current?.abort();listRequest.current?.abort();},[]);
  useEffect(()=>{
    const controller=new AbortController();
    setError('');
    api.competitions(controller.signal).then(data=>{setCompetitions(data.competitions || []);setNeedsAccess(false);}).catch(err=>{
      if(err.name!=='AbortError'){setError(err.message);if(err.status===401)setNeedsAccess(true);}
    });
    return ()=>controller.abort();
  },[reload]);
  const selectedName=useMemo(()=>competitions.find(item=>item.code===resultCompetition)?.name || resultCompetition,[competitions,resultCompetition]);
  const filtered=useMemo(()=>matches.filter(m=>(!teamQuery || normalize(`${m.home_team.name} ${m.away_team.name}`).includes(normalize(teamQuery))) && (!dateFilter || brazilDate(m.date)===dateFilter)).sort((a,b)=> (Date.parse(a.date)-Date.parse(b.date))*(sort==='asc'?1:-1)),[matches,teamQuery,dateFilter,sort]);
  const focus = ref => {ref.current?.focus({preventScroll:true});ref.current?.scrollIntoView?.({behavior:'smooth',block:'start'});};
  function closeAnalysis(){analysisRequest.current?.abort();setAnalysis(null);setAnalysisError('');setAnalysisLoading(false);if(selectedButton.current?.isConnected)selectedButton.current.focus();else focus(resultRegion);}
  async function loadMatches(event){
    event.preventDefault();listRequest.current?.abort();analysisRequest.current?.abort();
    const controller=new AbortController();listRequest.current=controller;
    setAnalysis(null);setAnalysisError('');setAnalysisLoading(false);setWarnings([]);setLoading(true);setError('');setMatches([]);setSearched(false);setTeamQuery('');setDateFilter('');
    try{const data=await api.matches(days,competition,controller.signal);if(controller.signal.aborted)return;setWarnings(data.warnings || []);setMatches(data.matches || []);setResultCompetition(competition);setSearched(true);}
    catch(err){if(err.name!=='AbortError'){setError(err.message+(err.retryAfter ? ` Tente novamente em ${err.retryAfter} segundos.` : ''));if(err.status===401)setNeedsAccess(true);}}
    finally{if(listRequest.current===controller)setLoading(false);}
  }
  async function loadAnalysis(id,event){
    selectedButton.current=event.currentTarget;analysisRequest.current?.abort();const controller=new AbortController();analysisRequest.current=controller;
    setAnalysis(null);setAnalysisError('');setAnalysisLoading(true);focus(analysisRegion);
    try{const data=await api.analysis(id,controller.signal);if(!controller.signal.aborted)setAnalysis(data);}
    catch(err){if(err.name!=='AbortError'){setAnalysisError(err.message+(err.retryAfter ? ` Tente novamente em ${err.retryAfter} segundos.` : ''));if(err.status===401)setNeedsAccess(true);}}
    finally{if(analysisRequest.current===controller)setAnalysisLoading(false);}
  }
  return <main>
    <header><a href="/" aria-label="BetAnalytics início">BetAnalytics</a><span className="badge">Futebol · análise descritiva</span></header>
    <section className="intro"><p className="eyebrow">HISTÓRICO EM CAMPO</p><h1>Conheça os números<br/>antes do próximo jogo.</h1><p>Compare equipes, forma recente e confrontos diretos. Dados históricos, com origem e limitações visíveis.</p></section>
    {needsAccess && <form className="access-form" onSubmit={e=>{e.preventDefault();setAccessToken(token);setToken('');setReload(v=>v+1);}}><h2>Acesso restrito</h2><p>Use o código de acesso fornecido pelo administrador.</p><label>Código de acesso<input type="password" autoComplete="off" required value={token} onChange={e=>setToken(e.target.value)}/></label><button>Entrar</button></form>}
    <form className="filters" onSubmit={loadMatches}>
      <label>Campeonato<select value={competition} onChange={e=>setCompetition(e.target.value)} disabled={loading || !competitions.length}>{!competitions.length && <option value="PL">Aguardando campeonatos...</option>}{competitions.map(item=><option key={item.code} value={item.code}>{item.name}</option>)}</select></label>
      <label>Período de busca<select value={days} onChange={e=>setDays(Number(e.target.value))} disabled={loading}><option value={3}>3 dias</option><option value={7}>7 dias</option><option value={14}>14 dias</option><option value={30}>30 dias</option></select></label>
      <button type="submit" disabled={loading || !competitions.length}>{loading?'Buscando...':'Buscar jogos'}</button>
    </form>
    <p className="filter-help">O período inclui hoje e usa datas UTC. Horários e filtro por data são exibidos em Brasília.</p>
    <section className="results" ref={resultRegion} tabIndex={-1} aria-label="Partidas disponíveis" aria-live="polite" aria-busy={loading}>
      <Warnings items={warnings}/>
      {error && <div className="message error" role="alert"><strong>Não foi possível carregar.</strong><span>{error}</span>{!competitions.length && !needsAccess && <button onClick={()=>setReload(v=>v+1)}>Tentar novamente</button>}</div>}
      {loading && <div className="message"><strong>Buscando partidas...</strong><button onClick={()=>{listRequest.current?.abort();setLoading(false);}}>Cancelar busca</button></div>}
      {!error && !loading && matches.length===0 && <div className="message"><strong>{searched?'Nenhuma partida futura encontrada.':'Nenhuma busca realizada.'}</strong><span>{searched?'Tente outro período ou campeonato. A cobertura depende da fonte esportiva.':'Selecione o campeonato e clique em Buscar jogos.'}</span></div>}
      {matches.length>0 && <>
        <div className="result-heading"><div><p className="eyebrow">{selectedName}</p><h2>{filtered.length} de {matches.length} partidas</h2></div><span>Horário de Brasília</span></div>
        <div className="local-filters"><label>Buscar time<input type="search" placeholder="Nome do time" value={teamQuery} onChange={e=>setTeamQuery(e.target.value)}/></label><label>Data em Brasília<input type="date" value={dateFilter} onChange={e=>setDateFilter(e.target.value)}/></label><label>Ordenar<select value={sort} onChange={e=>setSort(e.target.value)}><option value="asc">Mais próximas primeiro</option><option value="desc">Mais distantes primeiro</option></select></label><button className="secondary" onClick={()=>{setTeamQuery('');setDateFilter('');setSort('asc');}}>Limpar filtros</button></div>
        {!filtered.length && <p className="message">Nenhum jogo corresponde aos filtros. Limpe os filtros para ver todas as partidas carregadas.</p>}
        <div className="match-list">{filtered.map(match=><article className="match-card" key={match.id}>
          <div className="match-meta"><span>{match.competition.name}</span><time dateTime={match.date}>{formatDate(match.date)}</time></div>
          <div className="teams"><div><Crest team={match.home_team}/><strong>{match.home_team.name}</strong><small>Mandante</small></div><span className="versus">×</span><div><Crest team={match.away_team}/><strong>{match.away_team.name}</strong><small>Visitante</small></div></div>
          <button className="analysis-button" onClick={e=>loadAnalysis(match.id,e)}>Ver análise</button>
        </article>)}</div>
      </>}
    </section>
    <section className="analysis" ref={analysisRegion} tabIndex={-1} aria-label="Análise da partida" aria-live="polite" aria-busy={analysisLoading}>
      {(analysis || analysisLoading || analysisError) && <button className="secondary back-button" onClick={closeAnalysis}>Voltar às partidas</button>}
      {analysisLoading && <div className="message"><strong>Carregando análise...</strong><span>Consultando históricos das equipes e confrontos diretos.</span><button onClick={closeAnalysis}>Cancelar</button></div>}
      {analysisError && <div className="message error" role="alert">{analysisError}</div>}
      {analysis && <Analysis data={analysis}/>}
    </section>
    <footer>Dados fornecidos pela football-data.org. Estatísticas históricas não são previsões e não garantem resultados. Esta versão não utiliza IA.</footer>
  </main>;
}
createRoot(document.getElementById('root')).render(<React.StrictMode><App/></React.StrictMode>);
