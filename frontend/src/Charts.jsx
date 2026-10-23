import React from 'react';
const fmt = n => new Intl.NumberFormat('pt-BR', {maximumFractionDigits:2}).format(n);

export function ResultsChart({data}) {
  const n = data.matches_analyzed;
  return <figure className="chart"><figcaption>Resultados nos {n} jogos da amostra</figcaption>{n ? <>
    <div className="stacked-bar" aria-hidden="true">{[['wins','Vitórias'],['draws','Empates'],['losses','Derrotas']].map(([key,label]) => <span key={key} className={key} style={{width:`${100*data[key]/n}%`}} title={`${label}: ${data[key]}`}/>)}</div>
    <ul className="chart-legend">{[['wins','Vitórias'],['draws','Empates'],['losses','Derrotas']].map(([key,label])=><li key={key}><i className={key}/>{label}: <strong>{data[key]}</strong> ({fmt(100*data[key]/n)}%)</li>)}</ul>
  </> : <p>Sem amostra para calcular a distribuição.</p>}</figure>;
}
export function GoalsChart({home,away}) {
  const groups=[home,away];
  const max=Math.max(1,...groups.flatMap(t=>[t.average_goals_scored ?? 0,t.average_goals_conceded ?? 0]));
  return <section className="team-analysis goals-chart"><h3>Comparação de gols por jogo</h3><p>Médias nas amostras disponíveis. As barras usam a mesma escala.</p>{groups.map(t=><figure className="chart" key={t.team_id}><figcaption>{t.team} · {t.matches_analyzed} jogos</figcaption>{[['average_goals_scored','Marcados','scored'],['average_goals_conceded','Sofridos','conceded']].map(([key,label,color])=><div className="bar-row" key={key}><span>{label}</span><div className="bar-track" aria-hidden="true"><span className={color} style={{width:`${100*(t[key] ?? 0)/max}%`}}/></div><strong>{t[key] == null ? '—' : fmt(t[key])}</strong></div>)}{!t.matches_analyzed && <p>Dados indisponíveis; não representam zero gols.</p>}</figure>)}</section>;
}
export function VenueStats({data}) {
  return <details><summary>Desempenho em casa e fora</summary><p>Subgrupos dos últimos {data.matches_analyzed} jogos; não são dez jogos adicionais em cada condição.</p><div className="venue-grid">{[['home','Em casa'],['away','Fora de casa']].map(([key,label])=>{const t=data[key];return <div key={key}><h4>{label}</h4><p>{t.matches_analyzed} jogos</p>{t.matches_analyzed ? <><p>V / E / D: <strong>{t.wins} / {t.draws} / {t.losses}</strong></p><p>Gols marcados/jogo: <strong>{fmt(t.average_goals_scored)}</strong></p><p>Gols sofridos/jogo: <strong>{fmt(t.average_goals_conceded)}</strong></p></> : <p>Amostra indisponível.</p>}</div>;})}</div></details>;
}
