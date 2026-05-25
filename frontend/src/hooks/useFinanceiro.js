import { useState, useEffect } from 'react';
import api from '../services/api';
import { showToast } from '../components/ui/Toast';

export function useFinanceiro() {
  const [pendencias, setPendencias] = useState([]);
  const [pendenciasAdmin, setPendenciasAdmin] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingAdmin, setLoadingAdmin] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');
  const [errorAdmin, setErrorAdmin] = useState('');

  const fetchFinanceiro = async (mes) => {
    try {
      setLoading(true);
      const params = mes ? { mes } : {};
      const { data } = await api.get('/financeiro/me', { params });
      setPendencias(data);
    } catch (err) {
      setError('Erro ao buscar seus dados financeiros.');
    } finally {
      setLoading(false);
    }
  };

  const fetchFinanceiroAdmin = async (mes) => {
    try {
      setLoadingAdmin(true);
      const params = mes ? { mes } : {};
      const { data } = await api.get('/financeiro/admin', { params });
      setPendenciasAdmin(data);
    } catch (err) {
      setErrorAdmin('Erro ao buscar dados financeiros dos mensalistas.');
    } finally {
      setLoadingAdmin(false);
    }
  };

  const baixarPagamento = async (id, mes) => {
    try {
      setActionLoading(true);
      await api.put(`/financeiro/${id}/baixar`);
      // Recarrega os dados do jogador
      await fetchFinanceiro(mes);
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
      // Recarrega os dados do admin para o mês correspondente
      await fetchFinanceiroAdmin(mes);
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
  }, []);

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
    refetch: fetchFinanceiro,
    refetchAdmin: fetchFinanceiroAdmin
  };
}
