import { useState, useEffect } from 'react';
import api from '../services/api';

export function useRanking() {
  const [ranking, setRanking] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchRanking = async () => {
    try {
      setLoading(true);
      const { data } = await api.get('/ranking');
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

  return { ranking, loading, error, refetch: fetchRanking };
}
