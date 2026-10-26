import React, {useState} from 'react';
import {Crest, Icon} from './UI';
import {ResultsChart, GoalsChart, VenueStats} from './Charts';

export function formatDate(value) {
  if (!value || Number.isNaN(Date.parse(value))) return 'Não informado';
  return new Intl.DateTimeFormat('pt-BR', {dateStyle: 'short', timeStyle: 'short', timeZone: 'America/Sao_Paulo'}).format(new Date(value));
}
const number = (value) => value == null ? 'Indisponível' : new Intl.NumberFormat('pt-BR', {maximumFractionDigits: 2}).format(value);
const results = {W: 'Vitória', D: 'Empate', L: 'Derrota'};
const letters = {W: 'V', D: 'E', L: 'D'};
export function Warnings({items = []}) {
  return items.length > 0 && <aside className="message warning" role="status"><strong>Limitações dos dados</strong><details><summary>Ver {items.length} {items.length===1?'aviso':'avisos'} sobre esta consulta</summary><ul>{items.map((w, i) => <li key={i}>{({home:'Mandante', away:'Visitante', head_to_head:'Confrontos diretos'})[w.section] || w.section}: {w.code==='discarded_records'?'Alguns registros não atenderam aos critérios da análise e foram desconsiderados.':w.message}{w.retry_after ? ` Tente novamente em ${w.retry_after} segundos.` : ''}</li>)}</ul></details></aside>;
}
function History({rows = []}) {
  if (!rows.length) return <p>Nenhum jogo válido disponível.</p>;
  return <div className="table-wrap" tabIndex={0} role="region" aria-label="Histórico de jogos, tabela com rolagem horizontal"><table><caption>Jogos do mais recente ao mais antigo · tempo regulamentar</caption><thead><tr><th>Data (Brasília)</th><th>Competição</th><th>Mandante</th><th>Placar</th><th>Visitante</th></tr></thead><tbody>{rows.map(r => <tr key={r.id}><td>{formatDate(r.date)}</td><td>{r.competition.name || r.competition.code || r.competition.id}</td><td>{r.home_team}</td><td className="score">{r.home_score} × {r.away_score}</td><td>{r.away_team}</td></tr>)}</tbody></table></div>;
}
function Team({data, label, team}) {
  return <article className="team-analysis"><div className="team-card-heading"><Crest team={team}/><div><p className="eyebrow">{label}</p><h3>{data.team}</h3></div></div><p>{data.available ? `${data.matches_analyzed} de 10 jogos válidos disponíveis` : 'Histórico indisponível nesta consulta'}</p><dl className="metrics">{[
    ['Vitórias / empates / derrotas', data.matches_analyzed ? `${data.wins} / ${data.draws} / ${data.losses}` : 'Indisponível'],
    ['Gols marcados', number(data.goals_scored)], ['Gols sofridos', number(data.goals_conceded)],
    ['Média de gols marcados', number(data.average_goals_scored)], ['Média de gols sofridos', number(data.average_goals_conceded)],
    ['Média de gols totais por jogo', number(data.average_total_goals)],
    ['Ambas marcam', data.both_teams_scored == null ? 'Indisponível' : `${data.both_teams_scored} de ${data.matches_analyzed} jogos (${number(data.both_teams_scored_percentage)}%)`],
    ['Jogos sem sofrer gols', data.clean_sheets == null ? 'Indisponível' : `${data.clean_sheets} de ${data.matches_analyzed} jogos (${number(data.clean_sheet_percentage)}%)`],
    ['Vitórias no histórico', data.win_percentage == null ? 'Indisponível' : `${number(data.win_percentage)}%`],
  ].map(([name, value]) => <div key={name}><dt>{name}</dt><dd>{value}</dd></div>)}</dl>
    <ResultsChart data={data}/>
    <p>Forma recente (mais recente primeiro)</p><div className="form">{data.form.map((r,i) => <span className={`form-${r}`} key={i} title={results[r]} aria-label={results[r]}>{letters[r]}</span>)}</div>
    <p>Na amostra: {data.home.matches_analyzed} jogos em casa e {data.away.matches_analyzed} fora. A frequência histórica não é uma probabilidade para o próximo jogo.</p>
    <VenueStats data={data}/>
    
  </article>;
}
export default function Analysis({data}) {
  const [tab,setTab]=useState('overview');
  const h=data.head_to_head, home=data.home_team_analysis, away=data.away_team_analysis;
  const tabs=[['overview','Visão geral'],['history','Últimos jogos'],['h2h','Confrontos diretos'],['source','Origem dos dados']];
  return <div>
    <p className="eyebrow">ANÁLISE DA PARTIDA</p>
    <div className="fixture-hero panel"><div className="fixture-context"><span>{data.match.competition?.name || 'Futebol'}</span><span><Icon name="calendar" size={14}/>{formatDate(data.match.date)} · Brasília</span></div><div className="fixture-teams"><div><Crest team={data.match.home_team}/><h1>{data.match.home_team.name}</h1><span>Mandante</span></div><div className="fixture-vs">VS<small>PRÉ-JOGO</small></div><div><Crest team={data.match.away_team}/><h2>{data.match.away_team.name}</h2><span>Visitante</span></div></div><div className="fixture-bottom"><Icon name="chart" size={15}/>Análise descritiva · últimos jogos disponíveis</div></div>
    <Warnings items={data.warnings}/>
    <nav className="analysis-tabs" aria-label="Seções da análise">{tabs.map(([id,label])=><button key={id} aria-pressed={tab===id} className={tab===id?'selected':''} onClick={()=>setTab(id)}>{label}</button>)}</nav>
    {tab==='overview' && <>
      <div className="section-heading"><div><h2>O momento de cada equipe</h2><p>Até 10 jogos anteriores à partida, do mais recente ao mais antigo.</p></div><span className="subtle-tag">DADOS HISTÓRICOS</span></div>
      <div className="comparison"><Team data={home} team={data.match.home_team} label="Mandante"/><Team data={away} team={data.match.away_team} label="Visitante"/></div>
      <GoalsChart home={home} away={away}/>
      <div className="context-note"><Icon name="info"/><p>As equipes podem ter amostras de tamanhos diferentes. Os números descrevem esses jogos e não estimam a chance de vitória na próxima partida.</p></div>
    </>}
    {tab==='history' && <><div className="section-heading"><div><h2>Últimos jogos</h2><p>Resultados anteriores à partida selecionada. Placar do tempo regulamentar.</p></div></div>{[[home,'Mandante'],[away,'Visitante']].map(([t,label])=><section className="team-analysis history-section" key={label}><p className="eyebrow">{label}</p><h3>{t.team}</h3><p>{t.matches_analyzed} de 10 jogos válidos disponíveis</p><History rows={t.last_10}/></section>)}</>}
    {tab==='h2h' && <section className="team-analysis h2h-section"><p className="eyebrow">QUANDO SE ENCONTRARAM</p><h2>Confrontos diretos</h2><p>{h.available ? `${h.matches_analyzed} de 5 confrontos válidos disponíveis` : 'Confrontos indisponíveis nesta consulta'}</p>{h.matches_analyzed>0 && <><div className="h2h-stats"><div><strong>{h.home_team_wins}</strong><span>Vitórias · {data.match.home_team.name}</span></div><div><strong>{h.draws}</strong><span>Empates</span></div><div><strong>{h.away_team_wins}</strong><span>Vitórias · {data.match.away_team.name}</span></div><div><strong>{number(h.average_total_goals)}</strong><span>Média de gols totais</span></div></div></>}<History rows={h.matches}/></section>}
    {tab==='source' && <section className="team-analysis provenance"><p className="eyebrow">TRANSPARÊNCIA EM PRIMEIRO LUGAR</p><h2>Origem e qualidade dos dados</h2><p>Fonte: <strong>{data.metadata.source}</strong></p><dl className="source-grid"><div><dt>Corte:</dt><dd>{formatDate(data.metadata.cutoff)}</dd></div><div><dt>Gerado:</dt><dd>{formatDate(data.metadata.generated_at)}</dd></div>{Object.entries(data.metadata.retrieved_at).map(([key,value])=><div key={key}><dt>{({match:'Partida',home:'Mandante',away:'Visitante',head_to_head:'Confrontos'})[key] || key} · coleta</dt><dd>{formatDate(value)}</dd></div>)}</dl><div className="context-note"><Icon name="info"/><p>{data.metadata.historical_caveat}</p></div><p>Quando um dado não está disponível, isso é informado explicitamente. Ausência de dados não significa zero.</p></section>}
  </div>;
}
