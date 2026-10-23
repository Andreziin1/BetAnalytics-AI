import React from 'react';
import {ResultsChart, GoalsChart, VenueStats} from './Charts';

export function formatDate(value) {
  if (!value || Number.isNaN(Date.parse(value))) return 'Não informado';
  return new Intl.DateTimeFormat('pt-BR', {dateStyle: 'short', timeStyle: 'short', timeZone: 'America/Sao_Paulo'}).format(new Date(value));
}
const number = (value) => value == null ? 'Indisponível' : new Intl.NumberFormat('pt-BR', {maximumFractionDigits: 2}).format(value);
const results = {W: 'Vitória', D: 'Empate', L: 'Derrota'};
const letters = {W: 'V', D: 'E', L: 'D'};
export function Warnings({items = []}) {
  return items.length > 0 && <aside className="message warning" role="status"><strong>Limitações dos dados</strong><ul>{items.map((w, i) => <li key={i}>{({home:'Mandante', away:'Visitante', head_to_head:'Confrontos diretos'})[w.section] || w.section}: {w.message}{w.retry_after ? ` Tente novamente em ${w.retry_after} segundos.` : ''}</li>)}</ul></aside>;
}
function History({rows}) {
  if (!rows.length) return <p>Nenhum jogo válido disponível.</p>;
  return <div className="table-wrap" tabIndex={0} role="region" aria-label="Histórico de jogos, tabela com rolagem horizontal"><table><caption>Jogos do mais recente ao mais antigo · tempo regulamentar</caption><thead><tr><th>Data (Brasília)</th><th>Competição</th><th>Mandante</th><th>Placar</th><th>Visitante</th></tr></thead><tbody>{rows.map(r => <tr key={r.id}><td>{formatDate(r.date)}</td><td>{r.competition.name || r.competition.code || r.competition.id}</td><td>{r.home_team}</td><td className="score">{r.home_score} × {r.away_score}</td><td>{r.away_team}</td></tr>)}</tbody></table></div>;
}
function Team({data, label}) {
  return <article className="team-analysis"><p className="eyebrow">{label}</p><h3>{data.team}</h3><p>{data.available ? `${data.matches_analyzed} de 10 jogos válidos disponíveis` : 'Histórico indisponível nesta consulta'}</p><dl className="metrics">{[
    ['Vitórias / empates / derrotas', data.matches_analyzed ? `${data.wins} / ${data.draws} / ${data.losses}` : 'Indisponível'],
    ['Gols marcados', number(data.goals_scored)], ['Gols sofridos', number(data.goals_conceded)],
    ['Média de gols marcados', number(data.average_goals_scored)], ['Média de gols sofridos', number(data.average_goals_conceded)],
    ['Vitórias no histórico', data.win_percentage == null ? 'Indisponível' : `${number(data.win_percentage)}%`],
  ].map(([name, value]) => <div key={name}><dt>{name}</dt><dd>{value}</dd></div>)}</dl>
    <ResultsChart data={data}/>
    <p>Forma recente (mais recente primeiro)</p><div className="form">{data.form.map((r,i) => <span className={`form-${r}`} key={i} title={results[r]} aria-label={results[r]}>{letters[r]}</span>)}</div>
    <p>Na amostra: {data.home.matches_analyzed} jogos em casa e {data.away.matches_analyzed} fora. A frequência histórica não é uma probabilidade para o próximo jogo.</p>
    <VenueStats data={data}/>
    <details><summary>Ver histórico de {data.team}</summary><History rows={data.last_10}/></details>
  </article>;
}
export default function Analysis({data}) {
  const h = data.head_to_head;
  return <div><h2>{data.match.home_team.name} × {data.match.away_team.name}</h2><p>{formatDate(data.match.date)} · horário de Brasília</p><Warnings items={data.warnings}/><div className="comparison"><Team data={data.home_team_analysis} label="Mandante"/><Team data={data.away_team_analysis} label="Visitante"/></div>
    <GoalsChart home={data.home_team_analysis} away={data.away_team_analysis}/>
    <section className="team-analysis"><h3>Confrontos diretos</h3><p>{h.available ? `${h.matches_analyzed} de 5 confrontos válidos disponíveis` : 'Confrontos indisponíveis nesta consulta'}</p>{h.matches_analyzed > 0 && <><p>{data.match.home_team.name}: {h.home_team_wins} vitórias · Empates: {h.draws} · {data.match.away_team.name}: {h.away_team_wins} vitórias</p><p>Média de gols totais: {number(h.average_total_goals)}</p></>}<History rows={h.matches}/></section>
    <details className="provenance"><summary>Origem e qualidade dos dados</summary><p>Fonte: {data.metadata.source} · Corte: {formatDate(data.metadata.cutoff)} · Gerado: {formatDate(data.metadata.generated_at)}</p><ul>{Object.entries(data.metadata.retrieved_at).map(([key, value]) => <li key={key}>{({match:'Partida',home:'Mandante',away:'Visitante',head_to_head:'Confrontos'})[key]} — coletado: {formatDate(value)}</li>)}</ul><p>{data.metadata.historical_caveat}</p></details>
  </div>;
}
