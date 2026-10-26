import React, {useEffect, useMemo, useState, useRef} from 'react';
import {createRoot} from 'react-dom/client';
import {api} from './api';
import Analysis, {formatDate, Warnings} from './Analysis';
import {Icon, Crest, Brand} from './UI';
import './styles.css';

const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
export function brazilDate(value) {
  const parts = new Intl.DateTimeFormat('en-CA', {timeZone:'America/Sao_Paulo',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date(value));
  const get = type => parts.find(p => p.type === type).value;
  return `${get('year')}-${get('month')}-${get('day')}`;
}
function App() {
  const [analysisOpen,setAnalysisOpen]=useState(false);
  const [selectedMatch,setSelectedMatch]=useState(null);
  const [analysis,setAnalysis] = useState(null);
  const [analysisError,setAnalysisError] = useState('');
  const [analysisLoading,setAnalysisLoading] = useState(false);
  const [warnings,setWarnings] = useState([]);
  const analysisRequest=useRef(null), listRequest=useRef(null), analysisRegion=useRef(null), resultRegion=useRef(null), selectedButton=useRef(null);
  const [competitions,setCompetitions]=useState([]), [competition,setCompetition]=useState('PL'), [days,setDays]=useState(7);
  const [matches,setMatches]=useState([]), [loading,setLoading]=useState(false), [error,setError]=useState('');
  const [searched,setSearched]=useState(false), [resultCompetition,setResultCompetition]=useState('PL');
  const [teamQuery,setTeamQuery]=useState(''), [dateFilter,setDateFilter]=useState(''), [sort,setSort]=useState('asc');
  const [reload,setReload]=useState(0);
  useEffect(()=>()=>{analysisRequest.current?.abort();listRequest.current?.abort();},[]);
  useEffect(()=>{
    const controller=new AbortController();
    setError('');
    api.competitions(controller.signal).then(data=>setCompetitions(data.competitions || [])).catch(err=>{
      if(err.name!=='AbortError')setError(err.message);
    });
    return ()=>controller.abort();
  },[reload]);
  const selectedName=useMemo(()=>competitions.find(item=>item.code===resultCompetition)?.name || resultCompetition,[competitions,resultCompetition]);
  const filtered=useMemo(()=>matches.filter(m=>(!teamQuery || normalize(`${m.home_team.name} ${m.away_team.name}`).includes(normalize(teamQuery))) && (!dateFilter || brazilDate(m.date)===dateFilter)).sort((a,b)=> (Date.parse(a.date)-Date.parse(b.date))*(sort==='asc'?1:-1)),[matches,teamQuery,dateFilter,sort]);
  const focus = ref => {ref.current?.focus({preventScroll:true});ref.current?.scrollIntoView?.({behavior:'smooth',block:'start'});};
  useEffect(()=>{if(analysisOpen)focus(analysisRegion);else if(selectedButton.current?.isConnected)selectedButton.current.focus();},[analysisOpen]);
  function closeAnalysis(){setAnalysisOpen(false);analysisRequest.current?.abort();setAnalysis(null);setAnalysisError('');setAnalysisLoading(false);if(selectedButton.current?.isConnected)selectedButton.current.focus();else focus(resultRegion);}
  async function loadMatches(event, code=competition){
    event?.preventDefault();setCompetition(code);setAnalysisOpen(false);listRequest.current?.abort();analysisRequest.current?.abort();
    const controller=new AbortController();listRequest.current=controller;
    setAnalysis(null);setAnalysisError('');setAnalysisLoading(false);setWarnings([]);setLoading(true);setError('');setMatches([]);setSearched(false);setTeamQuery('');setDateFilter('');
    try{const data=await api.matches(days,code,controller.signal);if(controller.signal.aborted)return;setWarnings(data.warnings || []);setMatches(data.matches || []);setResultCompetition(code);setSearched(true);}
    catch(err){if(err.name!=='AbortError')setError(err.message+(err.retryAfter ? ` Tente novamente em ${err.retryAfter} segundos.` : ''));}
    finally{if(listRequest.current===controller)setLoading(false);}
  }
  async function loadAnalysis(id,event){
    if(event?.currentTarget)selectedButton.current=event.currentTarget;setSelectedMatch(matches.find(m=>m.id===id));setAnalysisOpen(true);analysisRequest.current?.abort();const controller=new AbortController();analysisRequest.current=controller;
    setAnalysis(null);setAnalysisError('');setAnalysisLoading(true);focus(analysisRegion);
    try{const data=await api.analysis(id,controller.signal);if(!controller.signal.aborted)setAnalysis(data);}
    catch(err){if(err.name!=='AbortError')setAnalysisError(err.message+(err.retryAfter ? ` Tente novamente em ${err.retryAfter} segundos.` : ''));}
    finally{if(analysisRequest.current===controller)setAnalysisLoading(false);}
  }
  const dates=[...new Set(matches.map(m=>brazilDate(m.date)))].sort();
  const groups=filtered.reduce((all,m)=>{const key=brazilDate(m.date);(all[key] ||= []).push(m);return all;},{});
  const dayLabel=value=>new Intl.DateTimeFormat('pt-BR',{weekday:'long',day:'numeric',month:'long',timeZone:'America/Sao_Paulo'}).format(new Date(value+'T12:00:00-03:00'));
  return <div className="app-shell">
    <a className="skip-link" href="#main-content">Pular para o conteúdo</a>
    <aside className="sidebar">
      <a className="brand-link" href="/" aria-label="BetAnalytics início"><Brand/></a>
      <div className="sidebar-section-label">EXPLORAR</div>
      <button className="nav-item active" onClick={closeAnalysis}><Icon name="ball"/>Partidas <span className="nav-dot"/></button>
      <div className="sidebar-section-label league-label">CAMPEONATOS <span>{competitions.length || '—'}</span></div>
      <nav className="league-nav" aria-label="Selecionar campeonato">{competitions.map(item=><button key={item.code} className={`league-item ${competition===item.code?'selected':''}`} aria-pressed={competition===item.code} onClick={e=>loadMatches(e,item.code)} disabled={loading}><span className="league-monogram">{item.code}</span><span>{item.name}</span>{competition===item.code && <Icon name="chevron" size={14}/>}</button>)}{!competitions.length && <p className="sidebar-hint">Os campeonatos aparecem após conectar ao servidor.</p>}</nav>
      <div className="sidebar-bottom"><Icon name="shield"/><strong>Dados, com contexto.</strong><p>Histórico real. Amostras visíveis.<br/>Sem promessas de resultado.</p><span>Fonte · football-data.org</span></div>
    </aside>
    <div className="workspace">
      <header className="topbar"><a className="mobile-brand brand-link" href="/" aria-label="BetAnalytics início"><Brand/></a><div className="breadcrumb"><Icon name="ball" size={18}/><span>Futebol</span><span>/</span><strong>{analysisOpen?'Análise da partida':'Central de partidas'}</strong></div><span className="timezone"><Icon name="clock" size={15}/>Horário de Brasília</span></header>
      <main id="main-content">
        <div hidden={analysisOpen}>
          <section className="page-heading"><div><p className="eyebrow">SEU PONTO DE PARTIDA</p><h1>O próximo jogo começa nos dados.</h1><p>Escolha uma partida. Compare os times. Entenda o histórico.</p></div><span className="sport-pill"><Icon name="ball" size={16}/>Futebol</span></section>
          <form className="filters panel" onSubmit={loadMatches}>
            <label>Campeonato<select value={competition} onChange={e=>setCompetition(e.target.value)} disabled={loading || !competitions.length}>{!competitions.length && <option value="PL">Aguardando campeonatos...</option>}{competitions.map(item=><option key={item.code} value={item.code}>{item.name}</option>)}</select></label>
            <label>Período de busca<select value={days} onChange={e=>setDays(Number(e.target.value))} disabled={loading}><option value={3}>Próximos 3 dias</option><option value={7}>Próximos 7 dias</option><option value={14}>Próximos 14 dias</option><option value={30}>Próximos 30 dias</option></select></label>
            <button type="submit" disabled={loading || !competitions.length}><Icon name="search" size={18}/>{loading?'Buscando...':'Buscar jogos'}</button>
          </form>
          <p className="filter-help"><Icon name="info" size={14}/>A busca inclui hoje e usa datas UTC. Os jogos abaixo são exibidos no horário de Brasília.</p>
          <div className="dashboard-grid">
            <section className="results" ref={resultRegion} tabIndex={-1} aria-label="Partidas disponíveis" aria-live="polite" aria-busy={loading}>
              <Warnings items={warnings}/>
              {error && <div className="message error" role="alert"><Icon name="info"/><strong>Não foi possível carregar.</strong><span>{error}</span><button className="secondary" onClick={competitions.length ? loadMatches : ()=>setReload(v=>v+1)}>Tentar novamente</button></div>}
              {loading && <div className="panel loading-panel"><div className="loading-caption" role="status"><span className="spinner"/><div><strong>Buscando partidas...</strong><p>Consultando o calendário da competição.</p></div></div>{[1,2,3,4].map(i=><div className="skeleton-row" key={i}><span/><span/><span/></div>)}<button className="secondary" onClick={()=>{listRequest.current?.abort();setLoading(false);}}>Cancelar busca</button></div>}
              {!error && !loading && matches.length===0 && <div className="panel empty-state"><span className="empty-icon"><Icon name={searched?'calendar':'ball'} size={34}/></span><p className="eyebrow">{searched?'CALENDÁRIO DA COMPETIÇÃO':'TUDO COMEÇA COM UMA PARTIDA'}</p><h2>{searched?'Nenhuma partida futura encontrada.':'Qual jogo vamos analisar?'}</h2><p>{searched?'Tente outro período ou campeonato. A cobertura depende da fonte esportiva.':'Selecione um campeonato e clique em Buscar jogos para explorar as próximas partidas.'}</p><div className="empty-steps"><span><b>01</b> Escolha a liga</span><span><b>02</b> Encontre o jogo</span><span><b>03</b> Compare os dados</span></div></div>}
              {matches.length>0 && <div className="panel matches-panel">
                <div className="result-heading"><div><p className="eyebrow">PRÓXIMAS PARTIDAS</p><h2>{selectedName}</h2></div><span className="count-pill">{filtered.length} de {matches.length} jogos</span></div>
                <div className="local-filters"><label className="search-label"><span>Buscar time</span><div className="input-icon"><Icon name="search" size={17}/><input type="search" placeholder="Buscar por time..." value={teamQuery} onChange={e=>setTeamQuery(e.target.value)}/></div></label><label>Data em Brasília<input type="date" value={dateFilter} onChange={e=>setDateFilter(e.target.value)}/></label><label>Ordenar<select value={sort} onChange={e=>setSort(e.target.value)}><option value="asc">Mais próximas</option><option value="desc">Mais distantes</option></select></label></div>
                <div className="date-toolbar"><div className="date-chips" aria-label="Filtrar por dia"><button className={!dateFilter?'selected':''} aria-pressed={!dateFilter} onClick={()=>setDateFilter('')}>Todos os dias</button>{dates.map(d=><button key={d} className={dateFilter===d?'selected':''} aria-pressed={dateFilter===d} onClick={()=>setDateFilter(d)}>{new Intl.DateTimeFormat('pt-BR',{day:'2-digit',month:'2-digit'}).format(new Date(d+'T12:00:00'))}</button>)}</div><button className="text-button" onClick={()=>{setTeamQuery('');setDateFilter('');setSort('asc');}}>Limpar filtros</button></div>
                {!filtered.length && <div className="empty-filter"><Icon name="search"/><p>Nenhum jogo corresponde aos filtros. Limpe os filtros para ver todas as partidas carregadas.</p></div>}
                <div className="match-list">{Object.entries(groups).map(([date,rows])=><section className="match-day" key={date}><h3><Icon name="calendar" size={14}/>{dayLabel(date)}<span>{rows.length} {rows.length===1?'jogo':'jogos'}</span></h3>{rows.map(match=><article className="match-card" key={match.id}>
                  <time dateTime={match.date}>{new Intl.DateTimeFormat('pt-BR',{timeZone:'America/Sao_Paulo',hour:'2-digit',minute:'2-digit'}).format(new Date(match.date))}</time>
                  <div className="match-teams"><div><Crest team={match.home_team}/><strong>{match.home_team.name}</strong><small>Mandante</small></div><div><Crest team={match.away_team}/><strong>{match.away_team.name}</strong><small>Visitante</small></div></div>
                  <button className="analysis-button" onClick={e=>loadAnalysis(match.id,e)}>Ver análise<Icon name="arrow" size={16}/></button>
                </article>)}</section>)}</div>
                <div className="list-footnote"><Icon name="clock" size={14}/>Datas e horários de Brasília · somente partidas futuras</div>
              </div>}
            </section>
            <aside className="insights-rail" aria-label="Sobre a análise"><section className="insight-card"><span className="insight-icon"><Icon name="chart" size={24}/></span><p className="eyebrow">ALÉM DO PLACAR</p><h2>Menos achismo.<br/>Mais contexto.</h2><p>O resultado conta uma parte da história. Veja o que aconteceu antes dele.</p><div className="scope-metric"><strong>10</strong><span>últimos jogos<br/>por equipe</span></div><div className="scope-metric"><strong>05</strong><span>últimos confrontos<br/>entre os times</span></div><small>Até esses limites, conforme a disponibilidade da fonte.</small></section><section className="method-card"><h3><Icon name="info" size={18}/>Como ler a análise</h3><p><b>Forma recente</b><br/>Vitórias, empates e derrotas da amostra.</p><p><b>Casa e fora</b><br/>O desempenho em cada condição.</p><p><b>Gols por jogo</b><br/>Médias para comparar as equipes.</p><div className="method-note">Frequência histórica não é probabilidade do próximo resultado.</div></section></aside>
          </div>
        </div>
        <section hidden={!analysisOpen} className="analysis" ref={analysisRegion} tabIndex={-1} aria-label="Análise da partida" aria-live="polite" aria-busy={analysisLoading}>
          <button className="text-button back-button" onClick={closeAnalysis}><Icon name="back" size={17}/>Voltar às partidas</button>
          {analysisLoading && <div className="panel empty-state"><span className="spinner"/><h2>Carregando análise...</h2><p>{selectedMatch?.home_team.name} × {selectedMatch?.away_team.name}</p><p>Consultando históricos das equipes e confrontos diretos.</p><button className="secondary" onClick={closeAnalysis}>Cancelar</button></div>}
          {analysisError && <div className="message error" role="alert"><strong>Não foi possível carregar a análise.</strong><span>{analysisError}</span><button className="secondary" onClick={()=>loadAnalysis(selectedMatch.id)}>Tentar novamente</button></div>}
          {analysis && <Analysis data={analysis}/>}
        </section>
        <footer><span>betanalytics <span>· Futebol em perspectiva</span></span><p>Fonte: football-data.org. Estatísticas históricas não garantem resultados. Esta versão não utiliza IA.</p></footer>
      </main>
    </div>
  </div>;
}
createRoot(document.getElementById('root')).render(<React.StrictMode><App/></React.StrictMode>);
