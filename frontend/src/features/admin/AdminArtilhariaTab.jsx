import React, { useState, useEffect } from 'react';
import api, { getFotoUrl } from '../../services/api';
import { showToast } from '../../components/ui/Toast';

export function AdminArtilhariaTab({ eventoId, presencas }) {
  const [jogadores, setJogadores] = useState([]);
  const [loading, setLoading] = useState({});

  useEffect(() => {
    if (presencas) {
      // Filtrar apenas jogadores com checkin validado (presentes)
      const presentes = presencas.filter(p => p.checkin_validado === true);
      
      // Mapear e ordenar por gols (maior para menor) e depois por nome
      const mapeados = presentes.map(p => ({
        usuario_id: p.usuario_id,
        nome: p.usuario_nome || 'Jogador',
        foto_url: p.usuario_foto_url,
        gols: p.gols || 0,
      })).sort((a, b) => {
        if (b.gols !== a.gols) return b.gols - a.gols;
        return a.nome.localeCompare(b.nome);
      });
      
      setJogadores(mapeados);
    }
  }, [presencas]);

  const handleAjustarGols = async (usuarioId, delta) => {
    setLoading(prev => ({ ...prev, [usuarioId]: true }));
    try {
      const response = await api.post(`/eventos/${eventoId}/presencas/${usuarioId}/gols`, { delta });
      const novosGols = response.data.gols;
      
      setJogadores(prev => 
        prev.map(j => j.usuario_id === usuarioId ? { ...j, gols: novosGols } : j)
      );
    } catch (err) {
      console.error("Erro ao ajustar gols", err);
      showToast("Erro ao ajustar gols do jogador", "error");
    } finally {
      setLoading(prev => ({ ...prev, [usuarioId]: false }));
    }
  };

  if (!presencas || presencas.length === 0) {
    return (
      <div className="text-center py-12 px-4 glass-panel rounded-2xl border-dashed border-2 border-outline-variant/50">
        <p className="text-on-surface-variant text-sm">
          Ainda não há presenças registradas para este evento.
        </p>
      </div>
    );
  }

  if (jogadores.length === 0) {
    return (
      <div className="text-center py-12 px-4 glass-panel rounded-2xl border-dashed border-2 border-outline-variant/50">
        <p className="text-on-surface-variant text-sm">
          Nenhum jogador confirmou presença nesta pelada ainda.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-primary text-[28px]">sports_soccer</span>
          <h2 className="font-headline-md text-headline-md font-bold text-on-surface">Artilharia da Pelada</h2>
        </div>
        <span className="bg-surface-variant text-on-surface-variant text-xs font-bold px-3 py-1 rounded-full">
          {jogadores.length} jogadores em campo
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {jogadores.map((jogador) => (
          <div key={jogador.usuario_id} className="glass-panel rounded-xl p-3 flex items-center justify-between shadow-ambient-1 hover:shadow-ambient-2 transition-shadow">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-surface-variant flex items-center justify-center text-on-surface-variant font-bold overflow-hidden shrink-0 border border-outline-variant/30">
                {jogador.foto_url ? (
                  <img src={getFotoUrl(jogador.foto_url)} alt={jogador.nome} className="w-full h-full object-cover" />
                ) : (
                  jogador.nome.charAt(0)
                )}
              </div>
              <div>
                <span className="font-bold text-on-surface block text-[15px]">{jogador.nome}</span>
                <span className="text-xs text-primary font-bold flex items-center gap-1">
                  {jogador.gols} {jogador.gols === 1 ? 'gol' : 'gols'}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-1 bg-surface-container rounded-lg p-1">
              <button
                onClick={() => handleAjustarGols(jogador.usuario_id, -1)}
                disabled={loading[jogador.usuario_id] || jogador.gols <= 0}
                className="w-8 h-8 flex items-center justify-center rounded-md bg-surface hover:bg-surface-variant disabled:opacity-30 transition-colors text-on-surface-variant"
              >
                <span className="material-symbols-outlined text-[20px]">remove</span>
              </button>
              
              <div className="w-8 flex items-center justify-center font-bold text-[16px] text-on-surface">
                {loading[jogador.usuario_id] ? (
                  <div className="w-4 h-4 rounded-full border-2 border-primary border-t-transparent animate-spin"></div>
                ) : (
                  jogador.gols
                )}
              </div>

              <button
                onClick={() => handleAjustarGols(jogador.usuario_id, 1)}
                disabled={loading[jogador.usuario_id]}
                className="w-8 h-8 flex items-center justify-center rounded-md bg-primary text-on-primary hover:bg-primary/90 disabled:opacity-50 transition-colors shadow-sm"
              >
                <span className="material-symbols-outlined text-[20px]">add</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
