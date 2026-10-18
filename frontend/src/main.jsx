import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { api } from './api';
import './styles.css';

function formatDate(value) {
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short', timeStyle: 'short', timeZone: 'America/Sao_Paulo',
  }).format(new Date(value));
}

function App() {
  const [competitions, setCompetitions] = useState([]);
  const [competition, setCompetition] = useState('PL');
  const [days, setDays] = useState(7);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searched, setSearched] = useState(false);
  const [resultCompetition, setResultCompetition] = useState('PL');

  useEffect(() => {
    const controller = new AbortController();
    api.competitions(controller.signal)
      .then((data) => setCompetitions(data.competitions || []))
      .catch((err) => {
        if (err.name !== 'AbortError') setError(err.message);
      });
    return () => controller.abort();
  }, []);

  const selectedName = useMemo(
    () => competitions.find((item) => item.code === resultCompetition)?.name || resultCompetition,
    [competitions, resultCompetition],
  );

  async function loadMatches(event) {
    event.preventDefault();
    setLoading(true);
    setError('');
    setMatches([]);
    setSearched(false);
    try {
      const data = await api.matches(days, competition);
      setMatches(data.matches || []);
      setResultCompetition(competition);
      setSearched(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return <main>
    <header>
      <a href="/" aria-label="BetAnalytics IA início">BetAnalytics <span>IA</span></a>
      <span className="badge">Futebol · análise descritiva</span>
    </header>
    <section className="intro">
      <p className="eyebrow">PARTIDAS FUTURAS</p>
      <h1>Escolha o campeonato<br/>e encontre o jogo.</h1>
      <p>Consulte partidas reais disponíveis na fonte esportiva. Os horários aparecem no fuso de Brasília.</p>
    </section>
    <form className="filters" onSubmit={loadMatches}>
      <label>Campeonato
        <select value={competition} onChange={(event) => setCompetition(event.target.value)} disabled={loading || !competitions.length}>
          {!competitions.length && <option>Carregando campeonatos...</option>}
          {competitions.map((item) => <option key={item.code} value={item.code}>{item.name}</option>)}
        </select>
      </label>
      <label>Próximos dias
        <select value={days} onChange={(event) => setDays(Number(event.target.value))} disabled={loading}>
          <option value={3}>3 dias</option><option value={7}>7 dias</option>
          <option value={14}>14 dias</option><option value={30}>30 dias</option>
        </select>
      </label>
      <button type="submit" disabled={loading || !competitions.length}>{loading ? 'Buscando...' : 'Buscar jogos'}</button>
    </form>
    <section className="results" aria-live="polite">
      {error && <div className="message error"><strong>Não foi possível carregar.</strong><span>{error}</span></div>}
      {!error && !loading && matches.length === 0 && <div className="message"><strong>{searched ? 'Nenhuma partida futura encontrada.' : 'Nenhuma busca realizada.'}</strong><span>{searched ? 'Tente outro período ou campeonato. A cobertura depende da fonte esportiva.' : 'Selecione o campeonato e clique em Buscar jogos.'}</span></div>}
      {matches.length > 0 && <>
        <div className="result-heading"><div><p className="eyebrow">{selectedName}</p><h2>{matches.length} {matches.length === 1 ? 'partida encontrada' : 'partidas encontradas'}</h2></div><span>Horário de Brasília</span></div>
        <div className="match-list">
          {matches.map((match) => <article className="match-card" key={match.id}>
            <div className="match-meta"><span>{match.competition.name}</span><time dateTime={match.date}>{formatDate(match.date)}</time></div>
            <div className="teams">
              <div><img src={match.home_team.crest} alt=""/><strong>{match.home_team.name}</strong><small>Mandante</small></div>
              <span className="versus">×</span>
              <div><img src={match.away_team.crest} alt=""/><strong>{match.away_team.name}</strong><small>Visitante</small></div>
            </div>
            <a className="analysis-link" href={api.analysisUrl(match.id)} target="_blank" rel="noreferrer">Ver análise em JSON <span>ID {match.id}</span></a>
          </article>)}
        </div>
      </>}
    </section>
    <footer>Dados fornecidos pela football-data.org. A análise usa histórico esportivo e não garante resultados.</footer>
  </main>;
}
createRoot(document.getElementById('root')).render(<React.StrictMode><App/></React.StrictMode>);

