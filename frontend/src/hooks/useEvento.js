import { useState, useEffect } from 'react';
import api from '../services/api';
import { showToast } from '../components/ui/Toast';

export function useEvento(eventoId = 1) {
  const [currentEventoId, setCurrentEventoId] = useState(eventoId);
  const [evento, setEvento] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchEvento = async () => {
    try {
      setLoading(true);
      setError('');
      
      let targetId = eventoId;
      
      // Se tivermos apenas o ID 1 por padrão, vamos tentar descobrir o mais recente
      if (targetId === 1) {
        try {
          const listResponse = await api.get('/eventos');
          const eventos = listResponse.data;
          if (eventos && eventos.length > 0) {
            // Pega o último evento criado (maior ID)
            const sorted = eventos.sort((a, b) => b.id - a.id);
            targetId = sorted[0].id;
          }
        } catch (e) {
          console.error("Erro ao listar eventos, caindo para id 1", e);
        }
      }

      const { data } = await api.get(`/eventos/${targetId}`);
      
      // Update global current ID if it changed
      if (targetId !== 1) {
          setCurrentEventoId(targetId);
      }
      
      setEvento(data);
    } catch (err) {
      if (err.response?.status === 404) {
        setEvento(null); // Nenhum evento ativo
      } else {
        setError('Erro ao carregar dados do evento. Tente novamente mais tarde.');
      }
    } finally {
      setLoading(false);
    }
  };

  const atualizarPresenca = async (status, posicao = 'LINHA', churrasco = false) => {
    try {
      setActionLoading(true);
      setError('');
      await api.put(`/eventos/${currentEventoId}/presencas/me`, { 
        status, 
        posicao, 
        churrasco 
      });
      await fetchEvento(); // Atualiza a lista em tempo real
      showToast('Presença atualizada com sucesso!');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao atualizar sua presença.';
      setError(msg);
      showToast(msg, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const criarEvento = async (payload) => {
    try {
      setActionLoading(true);
      await api.post(`/eventos`, payload);
      await fetchEvento();
      showToast('Partida criada com sucesso!');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao criar evento.';
      showToast(msg, 'error');
      throw err;
    } finally {
      setActionLoading(false);
    }
  };

  const iniciarVotacao = async () => {
    try {
      setActionLoading(true);
      await api.put(`/eventos/${currentEventoId}/iniciar-votacao`);
      await fetchEvento();
      showToast('Votação iniciada!');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao iniciar votação.';
      showToast(msg, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const encerrarVotacao = async () => {
    try {
      setActionLoading(true);
      await api.put(`/eventos/${currentEventoId}/encerrar`);
      await fetchEvento();
      showToast('Evento encerrado com sucesso!');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao encerrar votação.';
      showToast(msg, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  useEffect(() => {
    fetchEvento();
  }, [currentEventoId]);

  const atualizarChurrasco = async (flag_churrasco, valor_churrasco) => {
    try {
      setActionLoading(true);
      await api.put(`/eventos/${currentEventoId}/churrasco`, { flag_churrasco, valor_churrasco });
      await fetchEvento();
      showToast('Churrasco configurado com sucesso!');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao configurar churrasco.';
      showToast(msg, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const cancelarEvento = async () => {
    try {
      setActionLoading(true);
      await api.put(`/eventos/${currentEventoId}/cancelar`);
      await fetchEvento();
      showToast('Evento cancelado!');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao cancelar evento.';
      showToast(msg, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const sortearTimes = async (criterio = "NOTA_ADMIN") => {
    try {
      setActionLoading(true);
      const { data } = await api.post(`/eventos/${currentEventoId}/sorteio`, { criterio });
      showToast('Sorteio realizado!');
      return data; // Retorna os times montados
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao sortear times.';
      showToast(msg, 'error');
      return null;
    } finally {
      setActionLoading(false);
    }
  };

  const atualizarChavePix = async (chave_pix) => {
    try {
      setActionLoading(true);
      await api.put(`/eventos/${currentEventoId}/chave-pix`, { chave_pix });
      await fetchEvento();
      showToast('Chave Pix atualizada com sucesso!');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao atualizar chave Pix.';
      showToast(msg, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const atualizarMensalidade = async (valor_mensalidade) => {
    try {
      setActionLoading(true);
      await api.put(`/eventos/${currentEventoId}/mensalidade`, { valor_mensalidade });
      await fetchEvento();
      showToast('Mensalidade configurada com sucesso!');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao configurar mensalidade.';
      showToast(msg, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  return { 
    evento, 
    loading, 
    actionLoading, 
    error, 
    atualizarPresenca, 
    criarEvento,
    iniciarVotacao,
    encerrarVotacao,
    atualizarChurrasco,
    atualizarChavePix,
    atualizarMensalidade,
    cancelarEvento,
    sortearTimes,
    refetch: fetchEvento 
  };
}
