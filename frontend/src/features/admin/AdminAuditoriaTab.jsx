import React, { useState, useEffect } from 'react';
import api from '../../services/api';

export function AdminAuditoriaTab({ eventoId }) {
  const [auditoria, setAuditoria] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAuditoria = async () => {
      try {
        const response = await api.get(`/eventos/${eventoId}/votos-auditoria`);
        setAuditoria(response.data);
      } catch (err) {
        console.error("Erro ao buscar auditoria de votos", err);
      } finally {
        setLoading(false);
      }
    };
    
    if (eventoId) fetchAuditoria();
  }, [eventoId]);

  if (loading) {
    return <div className="py-10 flex justify-center"><div className="animate-spin rounded-full h-8 w-8 border-4 border-primary border-t-transparent"></div></div>;
  }

  if (auditoria.length === 0) {
    return (
      <div className="text-center py-12 px-4 glass-panel rounded-2xl border-dashed border-2 border-outline-variant/50">
        <div className="w-16 h-16 bg-surface-variant rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="material-symbols-outlined text-[32px] text-tertiary">how_to_vote</span>
        </div>
        <h3 className="text-[18px] font-bold text-on-surface mb-2">Nenhum voto registrado</h3>
        <p className="text-on-surface-variant text-sm max-w-xs mx-auto">
          Ainda não há votos registrados para este evento.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-2 mb-4">
        <span className="material-symbols-outlined text-primary text-[28px]">policy</span>
        <h2 className="font-headline-md text-headline-md font-bold text-on-surface">Auditoria de Votos</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {auditoria.map((item, index) => (
          <div key={index} className="glass-panel rounded-xl p-4 shadow-ambient-1 flex flex-col h-full border border-outline-variant/30 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1 h-full bg-primary/40"></div>
            
            <div className="flex items-center gap-2 border-b border-outline-variant/20 pb-3 mb-3">
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold shrink-0">
                {item.votante.charAt(0)}
              </div>
              <h3 className="font-bold text-[16px] text-on-background truncate">{item.votante}</h3>
              <span className="ml-auto text-[10px] font-bold px-2 py-0.5 bg-surface-variant text-tertiary rounded-full">
                Votante
              </span>
            </div>
            
            <div className="space-y-4 flex-1">
              {Object.keys(item.categorias).length > 0 && (
                <div>
                  <h4 className="text-[11px] font-label-bold text-on-surface-variant uppercase tracking-wider mb-2 flex items-center gap-1">
                    <span className="material-symbols-outlined text-[14px]">category</span>
                    Categorias
                  </h4>
                  <div className="space-y-1.5">
                    {Object.entries(item.categorias).map(([cat, cand]) => (
                      <div key={cat} className="flex justify-between items-center bg-surface-container-low px-2 py-1.5 rounded text-sm">
                        <span className="text-tertiary font-medium">{cat.replace('_', ' ')}</span>
                        <span className="font-bold text-on-surface">{cand}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {Object.keys(item.notas).length > 0 && (
                <div>
                  <h4 className="text-[11px] font-label-bold text-on-surface-variant uppercase tracking-wider mb-2 flex items-center gap-1">
                    <span className="material-symbols-outlined text-[14px]">star</span>
                    Notas Técnicas
                  </h4>
                  <div className="space-y-1.5">
                    {Object.entries(item.notas).map(([cand, nota]) => (
                      <div key={cand} className="flex justify-between items-center bg-surface-container-low px-2 py-1.5 rounded text-sm">
                        <span className="font-medium text-on-surface truncate pr-2">{cand}</span>
                        <span className="font-bold text-primary bg-primary/10 px-2 py-0.5 rounded">{nota}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
