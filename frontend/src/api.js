// A chave esportiva permanece somente no backend.
const base = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '');
async function get(path, signal) {
  const controller = new AbortController();
  const abort = () => controller.abort();
  const timer = setTimeout(abort, 190000);
  if (signal?.aborted) abort();
  else signal?.addEventListener('abort', abort, {once: true});
  let response;
  let data;
  try {
    response = await fetch(base + path, {signal: controller.signal});
    try {
      data = await response.json();
    } catch {
      throw new Error('O backend não respondeu com dados válidos. Tente novamente em instantes.');
    }
  } catch (error) {
    if (signal?.aborted) throw new DOMException('Consulta cancelada.', 'AbortError');
    if (controller.signal.aborted) throw new Error('A consulta demorou demais. Tente novamente.');
    if (error instanceof TypeError) throw new Error('Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.');
    throw error;
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', abort);
  }
  if (!response.ok) {
    const error = new Error(data?.error?.message || 'Não foi possível consultar os dados.');
    error.code = data?.error?.code;
    error.status = response.status;
    error.retryAfter = response.headers.get('Retry-After');
    throw error;
  }
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('Resposta inválida do servidor.');
  return data;
}
export const api = {
  analysisUrl: (id) => `${base}/matches/${id}/analysis`,
  health: (signal) => get('/health', signal),
  competitions: (signal) => get('/competitions', signal),
  matches: (days=7, competitions='', signal) => get('/matches?' + new URLSearchParams({days:String(days), ...(competitions ? {competitions} : {})}), signal),
  analysis: (id, signal) => {
    if (!Number.isSafeInteger(id) || id <= 0) throw new Error('Partida inválida.');
    return get('/matches/' + id + '/analysis', signal);
  },
};

