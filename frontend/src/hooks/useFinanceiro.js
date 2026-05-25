import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import { showToast } from '../components/ui/Toast';

// Cache em nível de módulo
let globalFinanceiroCache = {};
let globalFinanceiroAdminCache = {};
let globalFinanceiroCacheTime = {};
let globalFinanceiroAdminCacheTime = {};
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
    if (!force && globalFinanceiroCache[key] && globalFinanceiroCacheTime[key] && (now - globalFinanceiroCacheTime[key] < CACHE_DURATION)) {
      setPendencias(globalFinanceiroCache[key]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const params = mes ? { mes } : {};
      const { data } = await api.get('/financeiro/me', { params });

      globalFinanceiroCache[key] = data;
      globalFinanceiroCacheTime[key] = now;
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

    if (!force && globalFinanceiroAdminCache[key] && globalFinanceiroAdminCacheTime[key] && (now - globalFinanceiroAdminCacheTime[key] < CACHE_DURATION)) {
      setPendenciasAdmin(globalFinanceiroAdminCache[key]);
      setLoadingAdmin(false);
      return;
    }

    try {
      setLoadingAdmin(true);
      const params = mes ? { mes } : {};
      const { data } = await api.get('/financeiro/admin', { params });

      globalFinanceiroAdminCache[key] = data;
      globalFinanceiroAdminCacheTime[key] = now;
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
      showToast('Pagamento baixado com sucesso!');
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
      showToast('Pagamento baixado com sucesso!');
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
