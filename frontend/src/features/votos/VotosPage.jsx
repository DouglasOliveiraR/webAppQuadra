import React, { useState, useMemo } from 'react';
import { useEvento } from '../../hooks/useEvento';
import api from '../../services/api';
import { showToast } from '../../components/ui/Toast';

const CATEGORIAS = [
  { id: 'BOLA_CHEIA', titulo: 'Bola Cheia', desc: 'O Craque', imgSrc: '/assets/golden_ball_3d.png', color: 'text-[#F59E0B]', bg: 'bg-[#FEF3C7]' },
  { id: 'GOL_BONITO', titulo: 'Gol+ Bonito', desc: 'Golaço', imgSrc: '/assets/top_corner_goal_3d.png', color: 'text-[#10B981]', bg: 'bg-[#DCFCE7]' },
  { id: 'BOLA_MURCHA', titulo: 'Bola Murcha', desc: 'O Bagre', imgSrc: '/assets/deflated_ball_3d.png', color: 'text-[#F43F5E]', bg: 'bg-[#FFE4E6]' },
  { id: 'LAFON', titulo: 'Lafon', desc: 'O Chorão', imgSrc: '/assets/cry_face_3d.png', color: 'text-[#EC4899]', bg: 'bg-[#FCE7F3]' },
];

export function VotosPage() {
  const { evento, loading, error: errorEvento, refetch } = useEvento(1);
  const [votosFeitos, setVotosFeitos] = useState({});
  const [loadingAction, setLoadingAction] = useState(null);
  const [errorAction, setErrorAction] = useState('');
  
  // Select modal state
  const [activeCategory, setActiveCategory] = useState(null);

  const currentUserId = useMemo(() => {
    const token = localStorage.getItem('token');
    if (!token) return null;

    try {
      const payloadBase64 = token.split('.')[1];
      const decodedPayload = JSON.parse(atob(payloadBase64));
      return parseInt(decodedPayload.sub);
    } catch (e) {
      console.error(e);
      return null;
    }
  }, []);

  const handleVotar = (categoria, candidato_id) => {
    setVotosFeitos(prev => ({ ...prev, [categoria]: candidato_id }));
    setActiveCategory(null);
  };

  const confirmarTodos = async () => {
    if (Object.keys(votosFeitos).length < CATEGORIAS.length) {
      showToast('Por favor, vote nas 4 categorias antes de continuar.', 'error');
      return;
    }
    
    setLoadingAction('confirming');
    try {
      const promises = Object.entries(votosFeitos).map(([catId, candId]) => 
        api.post(`/eventos/${evento.id}/votos`, { categoria: catId, candidato_id: candId })
      );
      await Promise.all(promises);
      
      showToast('Votos confirmados! Agora avalie a galera.');
      window.location.href = '/avaliacao-galera';
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao registrar votos.';
      setErrorAction(msg);
      showToast(msg, 'error');
    } finally {
      setLoadingAction(null);
    }
  };

  const candidatos = evento?.presencas?.filter(p => p.checkin_validado && p.usuario_id !== currentUserId && p.usuario_perfil !== 'AVULSO') || [];

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary border-t-transparent"></div>
      </div>
    );
  }

  if (evento?.usuario_ja_votou) {
    return (
      <div className="flex flex-col items-center justify-center gap-6 p-6 h-screen text-center bg-background text-on-surface">
        <div className="w-20 h-20 bg-primary/20 rounded-full flex items-center justify-center shadow-lg border border-primary">
          <span className="material-symbols-outlined text-[40px] text-primary" style={{fontVariationSettings: "'FILL' 1"}}>check_circle</span>
        </div>
        <div className="space-y-2">
          <h2 className="font-headline-lg-mobile text-headline-lg-mobile font-bold">Votação Concluída!</h2>
          <p className="font-body-md text-body-md text-on-surface-variant max-w-xs mx-auto">
            Seus votos para esta partida foram computados com sucesso.
          </p>
        </div>
      </div>
    );
  }
  
  if (evento?.status_evento !== 'VOTACAO_ABERTA') {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-background text-on-surface p-6 text-center">
        <span className="material-symbols-outlined text-[64px] text-on-surface-variant mb-4">lock</span>
        <h3 className="font-headline-md text-headline-md font-bold">Votação Fechada</h3>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-2 max-w-xs mx-auto">
          A votação ainda não foi liberada pelo administrador ou já foi encerrada.
        </p>
      </div>
    );
  }

  if (candidatos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-background text-on-surface p-6 text-center">
        <span className="material-symbols-outlined text-[64px] text-on-surface-variant mb-4">hourglass_empty</span>
        <h3 className="font-headline-md text-headline-md font-bold">Aguardando Votação</h3>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-2 max-w-xs mx-auto">
          A lista estará disponível após a validação do check-in dos jogadores pelo Administrador na quadra, e início do período de votação.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-background text-on-surface pb-32">
      <main className="flex-1 overflow-y-auto px-4 mt-6">
        
        {/* Context Header */}
        <div className="mb-8 text-center pt-2">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-surface shadow-bento mb-4 border border-outline/10">
            <span className="material-symbols-outlined text-4xl text-primary icon-fill">sports</span>
          </div>
          <h2 className="font-display-lg text-title-lg text-on-surface font-extrabold mb-2 tracking-tight">Fim de Jogo!<br/>Hora da Resenha.</h2>
          <p className="font-body-md text-body-md text-on-surface-variant">Deixe seus votos para registrar no ranking.</p>
        </div>

        {(errorEvento || errorAction) && (
          <div className="p-3 bg-error-container text-on-error-container text-body-sm rounded-2xl text-center font-medium border border-error/20 mb-6 shadow-sm">
            {errorEvento || errorAction}
          </div>
        )}

        {/* Voting Grid - Bento Style */}
        <div className="grid grid-cols-2 gap-4">
          {CATEGORIAS.map(cat => {
            const hasVoted = votosFeitos[cat.id];
            const candidatoVotado = hasVoted ? candidatos.find(c => c.usuario_id === hasVoted) : null;
            
            return (
              <div 
                key={cat.id} 
                onClick={() => !hasVoted && setActiveCategory(cat.id)}
                className={`bento-card p-4 relative transition-transform ${
                  hasVoted 
                    ? 'border-2 border-primary shadow-[0_0_20px_rgba(52,199,89,0.15)] bg-primary-container/20' 
                    : 'border border-outline/20 cursor-pointer hover:bg-surface-variant/50'
                }`}
              >
                <div className="absolute -top-3 -right-3 w-10 h-10 bg-surface rounded-full flex items-center justify-center z-10 shadow-sm border border-outline/10">
                  <img src={cat.imgSrc} alt={cat.titulo} className="w-6 h-6 object-contain" />
                </div>
                
                <div className="text-center mb-4 mt-2">
                  <h3 className={`font-headline-md text-body-lg font-bold uppercase tracking-wider ${cat.color}`}>{cat.titulo}</h3>
                  <p className="font-body-sm text-[11px] text-on-surface-variant">({cat.desc})</p>
                </div>
                
                <div className="flex flex-col items-center pb-2">
                  {hasVoted ? (
                    <>
                      <div className="w-16 h-16 rounded-full border-4 border-primary bg-surface flex items-center justify-center overflow-hidden mb-2 relative shadow-md">
                        <span className="font-bold text-on-surface text-xl">{candidatoVotado?.usuario_nome?.charAt(0) || '?'}</span>
                        <div className="absolute bottom-0 right-0 w-6 h-6 bg-primary rounded-full flex items-center justify-center border-2 border-surface">
                          <span className="material-symbols-outlined text-[14px] text-on-primary font-bold">check</span>
                        </div>
                      </div>
                      <span className="font-headline-md text-body-md font-bold text-on-surface truncate w-full text-center">{candidatoVotado?.usuario_nome}</span>
                    </>
                  ) : (
                    <>
                      <div className="w-14 h-14 rounded-full border-2 border-dashed border-outline-variant bg-surface-variant/30 flex items-center justify-center mb-2">
                        <span className="material-symbols-outlined text-on-surface-variant">add</span>
                      </div>
                      <span className="font-label-bold text-[11px] text-primary uppercase tracking-wider text-center font-bold">Escolher<br/>Jogador</span>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </main>

      {/* Select Modal */}
      {activeCategory && (
        <div className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm flex items-end justify-center">
          <div className="bg-surface w-full max-w-screen-md h-3/4 rounded-t-3xl border-t border-outline/20 flex flex-col animate-[slideUp_0.3s_ease-out] shadow-[0_-10px_40px_rgba(0,0,0,0.1)]">
            <div className="p-6 border-b border-outline/10 flex justify-between items-center bg-surface-variant/30 rounded-t-3xl">
              <div>
                <h3 className="font-headline-md text-title-lg text-on-surface font-bold">Escolher {CATEGORIAS.find(c=>c.id === activeCategory)?.titulo}</h3>
                <p className="font-body-sm text-sm text-on-surface-variant">Selecione o jogador na lista abaixo</p>
              </div>
              <button
                onClick={() => setActiveCategory(null)}
                className="w-10 h-10 rounded-full bg-surface text-on-surface-variant flex items-center justify-center shadow-sm border border-outline/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary active:scale-95 transition-transform"
                aria-label="Fechar"
              >
                <span className="material-symbols-outlined" aria-hidden="true">close</span>
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {candidatos.map(p => (
                <button 
                  key={p.usuario_id}
                  onClick={() => handleVotar(activeCategory, p.usuario_id)}
                  disabled={loadingAction !== null}
                  className="w-full bento-card border border-outline/10 p-4 flex items-center gap-4 hover:border-primary/50 text-left"
                >
                  <div className="w-12 h-12 rounded-full bg-surface-variant flex items-center justify-center font-bold text-on-surface-variant shrink-0 shadow-inner">
                    {p.usuario_nome?.charAt(0) || '?'}
                  </div>
                  <span className="font-headline-md text-body-lg font-bold text-on-surface flex-1">{p.usuario_nome}</span>
                  {loadingAction === `${activeCategory}-${p.usuario_id}` ? (
                     <div className="animate-spin h-6 w-6 border-2 border-primary border-t-transparent rounded-full"></div>
                  ) : (
                     <div className="w-8 h-8 rounded-full bg-surface-variant flex items-center justify-center">
                        <span className="material-symbols-outlined text-on-surface-variant text-sm">chevron_right</span>
                     </div>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Fixed Action Button */}
      {Object.keys(votosFeitos).length === CATEGORIAS.length && (
        <div className="fixed bottom-24 left-4 right-4 z-40 max-w-[500px] mx-auto">
          <button 
            onClick={confirmarTodos}
            className="w-full bg-primary text-on-primary font-headline-md text-[18px] font-bold py-4 px-6 rounded-full shadow-bento flex items-center justify-center gap-2 hover:bg-primary/90 transition-colors active:scale-95"
          >
            <span className="material-symbols-outlined icon-fill">lock_open</span>
            Concluir Votação
          </button>
        </div>
      )}
    </div>
  );
}
