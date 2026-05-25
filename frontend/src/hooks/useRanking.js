import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

// Cache em nível de módulo para persistir entre remontagens do hook
let globalRankingCache = null;
let globalRankingCacheTime = null;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutos

export function useRanking() {
  const [ranking, setRanking] = useState(globalRankingCache || []);
  const [loading, setLoading] = useState(!globalRankingCache);
  const [error, setError] = useState('');

  const fetchRanking = useCallback(async (force = false) => {
    const now = Date.now();

    // Impacto: Uso do cache evita recarregar dados do servidor ao navegar entre abas, melhorando a UX e reduzindo requests.
    if (!force && globalRankingCache && globalRankingCacheTime && (now - globalRankingCacheTime < CACHE_DURATION)) {
      setRanking(globalRankingCache);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const { data } = await api.get('/ranking');
      globalRankingCache = data;
      globalRankingCacheTime = now;
      setRanking(data);
    } catch (err) {
      setError('Erro ao carregar o ranking. Tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRanking();
  }, [fetchRanking]);

  return { ranking, loading, error, refetch: () => fetchRanking(true) };
}
