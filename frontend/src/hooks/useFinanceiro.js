import { useState, useEffect } from 'react';
import api from '../services/api';
import { showToast } from '../components/ui/Toast';

export function useFinanceiro() {
  const [pendencias, setPendencias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchFinanceiro = async () => {
    try {
      setLoading(true);
      const { data } = await api.get('/financeiro/me');
      setPendencias(data);
    } catch (err) {
      setError('Erro ao buscar seus dados financeiros.');
    } finally {
      setLoading(false);
    }
  };

  const baixarPagamento = async (id) => {
    try {
      setActionLoading(true);
      await api.put(`/financeiro/${id}/baixar`);
      // Atualiza o estado localmente sem refazer requisição
      setPendencias((prev) => 
      prev.map(item => item.id === id ? { ...item, status_pagamento: 'PAGO' } : item)
      );
      showToast('Pagamento baixado com sucesso!');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao dar baixa no pagamento.';
      setError(msg);
      showToast(msg, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  useEffect(() => {
    fetchFinanceiro();
  }, []);

  return { pendencias, loading, actionLoading, error, baixarPagamento, refetch: fetchFinanceiro };
}
