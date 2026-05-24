import { useState, useEffect } from 'react';
import api from '../services/api';
import { showToast } from '../components/ui/Toast';

// Cache global em memória (module scope)
let globalFinanceiroCache = null;
let globalFinanceiroCacheTime = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutos

export function useFinanceiro() {
  const [pendencias, setPendencias] = useState(globalFinanceiroCache || []);
  const [loading, setLoading] = useState(!globalFinanceiroCache);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchFinanceiro = async (force = false) => {
    const now = Date.now();
    if (!force && globalFinanceiroCache && (now - globalFinanceiroCacheTime < CACHE_TTL)) {
      setPendencias(globalFinanceiroCache);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      // Impacto: Implementação de cache no hook useFinanceiro, reduzindo as requisições na aba do Financeiro
      const { data } = await api.get('/financeiro/me');
      globalFinanceiroCache = data;
      globalFinanceiroCacheTime = Date.now();
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
      const novasPendencias = pendencias.map(item => item.id === id ? { ...item, status_pagamento: 'PAGO' } : item);
      setPendencias(novasPendencias);

      // Atualiza o cache também para refletir na próxima navegação
      if (globalFinanceiroCache) {
         globalFinanceiroCache = novasPendencias;
      }
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

  return { pendencias, loading, actionLoading, error, baixarPagamento, refetch: () => fetchFinanceiro(true) };
}
