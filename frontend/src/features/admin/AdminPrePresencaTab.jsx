import React, { useState, useEffect } from 'react';
import api, { getFotoUrl } from '../../services/api';
import { showToast } from '../../components/ui/Toast';

export function AdminPrePresencaTab({ eventoId }) {
  const [usuarios, setUsuarios] = useState([]);
  const [presencas, setPresencas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);

  const carregarDados = async () => {
    try {
      const [resUsuarios, resEvento] = await Promise.all([
        api.get('/usuarios'),
        api.get(`/eventos/${eventoId}`)
      ]);
      setUsuarios(resUsuarios.data);
      setPresencas(resEvento.data.presencas || []);
    } catch (err) {
      console.error(err);
      showToast('Erro ao carregar pré-presença', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    carregarDados();
  }, [eventoId]);

  const handleForcarStatus = async (usuarioId, status, posicaoAtual, churrascoAtual) => {
    setActionLoading(usuarioId);
    try {
      await api.put(`/eventos/${eventoId}/presencas/${usuarioId}/admin-status`, {
        status: status,
        posicao: posicaoAtual || 'LINHA',
        churrasco: churrascoAtual || false
      });
      showToast(`Status atualizado para ${status}`, 'success');
      await carregarDados();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao forçar status.';
      showToast(msg, 'error');
    } finally {
      setActionLoading(null);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Carregando jogadores...</div>;
  }

  // Mesclar usuarios com presencas
  const jogadoresComStatus = usuarios.map(u => {
    const p = presencas.find(pres => pres.usuario_id === u.id);
    return {
      ...u,
      status_jogo: p?.status_jogo || 'PENDENTE',
      posicao: p?.posicao || 'LINHA',
      vai_churrasco: p?.vai_churrasco || false,
      checkin_validado: p?.checkin_validado || false
    };
  });

  const pendentes = jogadoresComStatus.filter(j => j.status_jogo === 'PENDENTE');
  const confirmados = jogadoresComStatus.filter(j => j.status_jogo === 'VOU');
  const ausentes = jogadoresComStatus.filter(j => j.status_jogo === 'NAO_VOU');

  const renderCard = (jogador) => (
    <div key={jogador.id} className="glass-panel rounded-xl p-3 flex flex-col gap-2 shadow-ambient-1 mb-2">
      <div className="flex justify-between items-center border-b border-outline-variant/20 pb-2">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-surface-variant flex items-center justify-center text-on-surface-variant text-xs font-bold shrink-0 overflow-hidden">
            {jogador.foto_url ? (
              <img src={getFotoUrl(jogador.foto_url)} alt={jogador.nome} className="w-full h-full object-cover" />
            ) : (
              jogador.nome.charAt(0)
            )}
          </div>
          <span className="font-bold text-on-background text-[14px]">{jogador.nome}</span>
        </div>
        <div className="text-[10px] bg-surface-variant px-2 py-1 rounded-md text-on-surface-variant font-bold">
          {jogador.status_jogo}
        </div>
      </div>
      <div className="flex gap-2">
        <button 
          onClick={() => handleForcarStatus(jogador.id, 'PENDENTE', jogador.posicao, jogador.vai_churrasco)}
          disabled={actionLoading === jogador.id || jogador.status_jogo === 'PENDENTE'}
          className={`py-1.5 text-[10px] font-bold uppercase flex-1 rounded-lg transition-colors ${jogador.status_jogo === 'PENDENTE' ? 'bg-surface-variant text-on-surface' : 'border border-surface-variant text-on-surface-variant hover:bg-surface-container-high'}`}
        >
          <span className="material-symbols-outlined text-[14px] align-text-bottom mr-1">schedule</span>
          Pendente
        </button>
        <button 
          onClick={() => handleForcarStatus(jogador.id, 'VOU', jogador.posicao, jogador.vai_churrasco)}
          disabled={actionLoading === jogador.id || jogador.status_jogo === 'VOU'}
          className={`py-1.5 text-[10px] font-bold uppercase flex-1 rounded-lg transition-colors ${jogador.status_jogo === 'VOU' ? 'bg-primary text-on-primary' : 'border border-primary/50 text-primary hover:bg-primary/10'}`}
        >
          <span className="material-symbols-outlined text-[14px] align-text-bottom mr-1">check_circle</span>
          Vou
        </button>
        <button 
          onClick={() => handleForcarStatus(jogador.id, 'NAO_VOU', jogador.posicao, jogador.vai_churrasco)}
          disabled={actionLoading === jogador.id || jogador.status_jogo === 'NAO_VOU'}
          className={`py-1.5 text-[10px] font-bold uppercase flex-1 rounded-lg transition-colors ${jogador.status_jogo === 'NAO_VOU' ? 'bg-error text-white' : 'border border-error/50 text-error hover:bg-error/10'}`}
        >
          <span className="material-symbols-outlined text-[14px] align-text-bottom mr-1">cancel</span>
          Não Vou
        </button>
      </div>
    </div>
  );

  return (
    <div className="space-y-6 fade-in">
      <div className="bg-primary/10 border border-primary/20 rounded-xl p-4">
        <h3 className="font-headline-md text-primary text-[16px] mb-2">Pré-Presença (Modo Admin)</h3>
        <p className="text-[12px] text-on-surface-variant">
          Adicione na lista de presença jogadores que confirmaram no WhatsApp, mas não acessam o App. 
          Eles <strong>não ganharão pontos</strong> até você dar o Check-in real na quadra.
        </p>
      </div>

      <div>
        <h4 className="font-bold text-on-surface mb-3 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-tertiary"></span> Pendentes ({pendentes.length})
        </h4>
        {pendentes.map(renderCard)}
      </div>

      <div>
        <h4 className="font-bold text-on-surface mb-3 flex items-center gap-2 mt-4">
          <span className="w-2 h-2 rounded-full bg-primary"></span> Confirmados ({confirmados.length})
        </h4>
        {confirmados.map(renderCard)}
      </div>

      <div>
        <h4 className="font-bold text-on-surface mb-3 flex items-center gap-2 mt-4">
          <span className="w-2 h-2 rounded-full bg-error"></span> Ausentes ({ausentes.length})
        </h4>
        {ausentes.map(renderCard)}
      </div>
    </div>
  );
}
