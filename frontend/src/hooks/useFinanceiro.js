import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import { showToast } from '../components/ui/Toast';

// Cache em nível de módulo
let cacheJogador = {};
let cacheAdmin = {};
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutos

export function useFinanceiro() {
  const [pendencias, setPendencias] = useState([]);
  const [pendenciasAdmin, setPendenciasAdmin] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingAdmin, setLoadingAdmin] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');
  const [errorAdmin, setErrorAdmin] = useState('');

  const fetchFinanceiro = useCallback(async (mes, force = false) => {
    const key = mes || 'current';
    const now = Date.now();

    // Impacto: Uso do cache em useFinanceiro evita requests repetitivos na navegação, garantindo navegação instantânea.
    if (!force && cacheJogador[key]?.data && cacheJogador[key]?.timestamp && (now - cacheJogador[key].timestamp < CACHE_DURATION)) {
      setPendencias(cacheJogador[key].data);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const params = mes ? { mes } : {};
      if (force) params._t = Date.now();
      const { data } = await api.get('/financeiro/me', { params });

      cacheJogador[key] = { data, timestamp: now };
      setPendencias(data);
    } catch (err) {
      setError('Erro ao buscar seus dados financeiros.');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchFinanceiroAdmin = useCallback(async (mes, force = false) => {
    const key = mes || 'current';
    const now = Date.now();

    if (!force && cacheAdmin[key]?.data && cacheAdmin[key]?.timestamp && (now - cacheAdmin[key].timestamp < CACHE_DURATION)) {
      setPendenciasAdmin(cacheAdmin[key].data);
      setLoadingAdmin(false);
      return;
    }

    try {
      setLoadingAdmin(true);
      const params = mes ? { mes } : {};
      if (force) params._t = Date.now();
      const { data } = await api.get('/financeiro/admin', { params });

      cacheAdmin[key] = { data, timestamp: now };
      setPendenciasAdmin(data);
    } catch (err) {
      setErrorAdmin('Erro ao buscar dados financeiros dos mensalistas.');
    } finally {
      setLoadingAdmin(false);
    }
  }, []);

  const baixarPagamento = async (id, mes) => {
    try {
      setActionLoading(true);
      await api.put(`/financeiro/${id}/baixar`);
      // Recarrega os dados do jogador forçando o bypass do cache
      await fetchFinanceiro(mes, true);
      showToast('Status do pagamento atualizado!');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao dar baixa no pagamento.';
      setError(msg);
      showToast(msg, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const baixarPagamentoAdmin = async (id, mes) => {
    try {
      setActionLoading(true);
      await api.put(`/financeiro/${id}/baixar`);
      // Recarrega os dados do admin forçando o bypass do cache
      await fetchFinanceiroAdmin(mes, true);
      showToast('Status do pagamento atualizado!');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao dar baixa no pagamento.';
      setErrorAdmin(msg);
      showToast(msg, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  useEffect(() => {
    fetchFinanceiro();
  }, [fetchFinanceiro]);

  return { 
    pendencias, 
    pendenciasAdmin,
    loading, 
    loadingAdmin,
    actionLoading, 
    error, 
    errorAdmin,
    baixarPagamento, 
    baixarPagamentoAdmin,
    refetch: (mes) => fetchFinanceiro(mes, true),
    refetchAdmin: (mes) => fetchFinanceiroAdmin(mes, true)
  };
}
