import React, { useState, useMemo } from 'react';
import { useEvento } from '../../hooks/useEvento';
import api from '../../services/api';
import { showToast } from '../../components/ui/Toast';

const CATEGORIAS = [
  { id: 'BOLA_CHEIA', titulo: 'Bola Cheia', desc: 'O Craque', icon: 'star', color: 'text-yellow-400', bgIcon: 'text-yellow-400' },
  { id: 'GOL_BONITO', titulo: 'Gol+ Bonito', desc: 'Golaço', icon: 'sports_soccer', color: 'text-white', bgIcon: 'text-white' },
  { id: 'BOLA_MURCHA', titulo: 'Bola Murcha', desc: 'O Bagre', icon: 'arrow_downward', color: 'text-red-400', bgIcon: 'text-red-500' },
  { id: 'LAFON', titulo: 'Lafon', desc: 'O Paredão', icon: 'shield', color: 'text-blue-400', bgIcon: 'text-blue-400' },
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
      <div className="flex h-screen items-center justify-center bg-gray-900">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary-fixed border-t-transparent"></div>
      </div>
    );
  }

  if (evento?.usuario_ja_votou) {
    return (
      <div className="flex flex-col items-center justify-center gap-6 p-6 h-screen text-center bg-gray-950 text-white">
        <div className="w-20 h-20 bg-primary-fixed/20 rounded-full flex items-center justify-center shadow-lg border border-primary-fixed">
          <span className="material-symbols-outlined text-[40px] text-primary-fixed" style={{fontVariationSettings: "'FILL' 1"}}>check_circle</span>
        </div>
        <div className="space-y-2">
          <h2 className="font-headline-lg-mobile text-headline-lg-mobile font-bold">Votação Concluída!</h2>
          <p className="font-body-md text-body-md text-gray-400 max-w-xs">
            Seus votos para esta partida foram computados com sucesso.
          </p>
        </div>
      </div>
    );
  }
  
  if (evento?.status_evento !== 'VOTACAO_ABERTA') {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-950 text-white p-6 text-center">
        <span className="material-symbols-outlined text-[64px] text-gray-700 mb-4">lock</span>
        <h3 className="font-headline-md text-headline-md font-bold text-gray-200">Votação Fechada</h3>
        <p className="font-body-sm text-body-sm text-gray-400 mt-2">
          A votação ainda não foi liberada pelo administrador ou já foi encerrada.
        </p>
      </div>
    );
  }

  if (candidatos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-950 text-white p-6 text-center">
        <span className="material-symbols-outlined text-[64px] text-gray-700 mb-4">hourglass_empty</span>
        <h3 className="font-headline-md text-headline-md font-bold text-gray-200">Aguardando Votação</h3>
        <p className="font-body-sm text-body-sm text-gray-400 mt-2">
          A lista estará disponível após a validação do check-in dos jogadores pelo Administrador na quadra, e início do período de votação.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-gray-950 text-white -mt-20">
      <main className="flex-1 overflow-y-auto pt-24 px-container-margin-mobile pb-32">
        
        {/* Context Header */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/20 text-primary-fixed mb-4">
            <span className="material-symbols-outlined text-4xl">sports</span>
          </div>
          <h2 className="font-headline-lg-mobile text-headline-lg-mobile text-on-primary mb-2">Fim de Jogo!<br/>Hora da Resenha.</h2>
          <p className="font-body-md text-body-md text-gray-400">Deixe seus votos para registrar no ranking.</p>
        </div>

        {(errorEvento || errorAction) && (
          <div className="p-3 bg-red-900/50 text-red-200 text-body-sm rounded-lg text-center font-medium border border-red-500/50 mb-6">
            {errorEvento || errorAction}
          </div>
        )}

        {/* Voting Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {CATEGORIAS.map(cat => {
            const hasVoted = votosFeitos[cat.id];
            const candidatoVotado = hasVoted ? candidatos.find(c => c.usuario_id === hasVoted) : null;
            
            return (
              <div 
                key={cat.id} 
                onClick={() => !hasVoted && setActiveCategory(cat.id)}
                className={`rounded-xl p-3 relative transition-transform ${
                  hasVoted 
                    ? 'bg-gray-800 border border-primary-fixed/50 shadow-[0_0_15px_rgba(107,255,143,0.1)]' 
                    : 'bg-gray-800/50 border border-dashed border-gray-600 cursor-pointer hover:bg-gray-800 hover:scale-[1.02]'
                }`}
              >
                <div className="absolute -top-3 -right-3 w-8 h-8 bg-gray-900 rounded-full flex items-center justify-center z-10 border border-gray-800">
                  <span className={`material-symbols-outlined text-xl ${cat.bgIcon}`} style={hasVoted ? {fontVariationSettings: "'FILL' 1"} : {}}>{cat.icon}</span>
                </div>
                
                <div className="text-center mb-3">
                  <h3 className={`font-label-bold text-label-bold uppercase tracking-wider ${cat.color}`}>{cat.titulo}</h3>
                  <p className="font-body-sm text-[10px] text-gray-400">({cat.desc})</p>
                </div>
                
                <div className="flex flex-col items-center">
                  {hasVoted ? (
                    <>
                      <div className="w-16 h-16 rounded-full border-2 border-primary-fixed flex items-center justify-center bg-gray-700 overflow-hidden mb-2 relative">
                        <span className="font-bold text-white text-xl">{candidatoVotado?.usuario_nome?.charAt(0) || '?'}</span>
                        <div className="absolute bottom-0 right-0 w-5 h-5 bg-primary-container rounded-full flex items-center justify-center border-2 border-gray-800">
                          <span className="material-symbols-outlined text-[12px] text-on-primary-container font-bold">check</span>
                        </div>
                      </div>
                      <span className="font-label-bold text-label-bold text-on-primary truncate w-full text-center">{candidatoVotado?.usuario_nome?.split(' ')[0]}</span>
                    </>
                  ) : (
                    <>
                      <div className="w-16 h-16 rounded-full border-2 border-dashed border-gray-600 bg-gray-700/50 flex items-center justify-center mb-2">
                        <span className="material-symbols-outlined text-gray-400">add</span>
                      </div>
                      <span className="font-label-bold text-[10px] text-primary-fixed uppercase tracking-wider text-center">Escolher<br/>Jogador</span>
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
        <div className="fixed inset-0 z-[100] bg-black/80 flex items-end justify-center">
          <div className="bg-gray-900 w-full max-w-screen-md h-3/4 md:h-1/2 rounded-t-3xl border-t border-gray-700 flex flex-col animate-[slideUp_0.3s_ease-out]">
            <div className="p-4 border-b border-gray-800 flex justify-between items-center">
              <div>
                <h3 className="font-headline-md text-headline-md text-white">Escolher {CATEGORIAS.find(c=>c.id === activeCategory)?.titulo}</h3>
                <p className="font-body-sm text-sm text-gray-400">Selecione o jogador na lista abaixo</p>
              </div>
              <button onClick={() => setActiveCategory(null)} className="w-10 h-10 rounded-full bg-gray-800 text-gray-400 flex items-center justify-center">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              {candidatos.map(p => (
                <button 
                  key={p.usuario_id}
                  onClick={() => handleVotar(activeCategory, p.usuario_id)}
                  disabled={loadingAction !== null}
                  className="w-full bg-gray-800 border border-gray-700 hover:border-primary-fixed rounded-xl p-4 flex items-center gap-3 transition-colors text-left"
                >
                  <div className="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center font-bold text-white shrink-0">
                    {p.usuario_nome?.charAt(0) || '?'}
                  </div>
                  <span className="font-body-md font-semibold text-white flex-1">{p.usuario_nome}</span>
                  {loadingAction === `${activeCategory}-${p.usuario_id}` ? (
                     <div className="animate-spin h-5 w-5 border-2 border-primary-fixed border-t-transparent rounded-full"></div>
                  ) : (
                     <span className="material-symbols-outlined text-gray-500">chevron_right</span>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Fixed Action Button */}
      {Object.keys(votosFeitos).length === CATEGORIAS.length && (
        <div className="fixed bottom-20 left-4 right-4 z-40 max-w-screen-xl mx-auto md:px-container-margin-desktop">
          <button 
            onClick={confirmarTodos}
            className="w-full bg-primary-fixed text-on-primary-fixed font-headline-md text-[16px] font-bold py-4 px-6 rounded-xl shadow-[0_4px_20px_rgba(107,255,143,0.3)] flex items-center justify-center gap-2 hover:bg-inverse-primary transition-colors active:scale-95"
          >
            <span className="material-symbols-outlined">lock_open</span>
            Concluir Votação
          </button>
        </div>
      )}
    </div>
  );
}
