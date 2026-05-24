import { useState, useEffect } from 'react';
import api from '../services/api';

// Cache global em memória (module scope)
let globalRankingCache = null;
let globalRankingCacheTime = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutos

export function useRanking() {
  const [ranking, setRanking] = useState(globalRankingCache || []);
  const [loading, setLoading] = useState(!globalRankingCache);
  const [error, setError] = useState('');

  const fetchRanking = async (force = false) => {
    // Retorna do cache se não for forçado e ainda estiver dentro do TTL
    const now = Date.now();
    if (!force && globalRankingCache && (now - globalRankingCacheTime < CACHE_TTL)) {
      setRanking(globalRankingCache);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      // Impacto: Implementação de cache no hook useRanking, reduzindo as chamadas de rede redundantes durante a navegação entre abas
      const { data } = await api.get('/ranking');
      globalRankingCache = data;
      globalRankingCacheTime = Date.now();
      setRanking(data);
    } catch (err) {
      setError('Erro ao carregar o ranking. Tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRanking();
  }, []);

  return { ranking, loading, error, refetch: () => fetchRanking(true) };
}
