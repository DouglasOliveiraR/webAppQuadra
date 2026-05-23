import React, { useState, useEffect } from 'react';
import api from '../../services/api';

export function RankingPage() {
  const [ranking, setRanking] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRanking = async () => {
      try {
        const response = await api.get('/ranking');
        setRanking(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchRanking();
  }, []);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary border-t-transparent"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-error-container text-on-error-container m-4 rounded-xl">
        Erro ao carregar o ranking.
      </div>
    );
  }

  // Get Top 3 for Podium
  const sortedRanking = ranking ? [...ranking].sort((a, b) => b.pontos - a.pontos) : [];
  const top3 = sortedRanking.slice(0, 3);
  const restOfRanking = sortedRanking.slice(3);

  return (
    <div className="flex flex-col w-full pb-6">
      {/* Screen Title */}
      <div className="flex items-center gap-3 mb-6 mt-4">
        <div className="w-10 h-10 rounded-full flex items-center justify-center shadow-sm bg-primary-container text-on-primary-container">
          <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>trophy</span>
        </div>
        <h2 className="font-headline-md text-headline-md text-on-surface">Resenha & Ranking</h2>
      </div>

      {/* Tabs */}
      <div className="flex p-1 bg-surface-container-low rounded-lg mb-8 shadow-inner">
        <button className="flex-1 py-2 rounded-md bg-surface text-primary shadow-sm font-label-bold text-label-bold transition-all">Tabela Geral</button>
        <button className="flex-1 py-2 rounded-md text-on-surface-variant font-label-bold text-label-bold hover:bg-surface-container transition-all">Último Jogo</button>
      </div>

      {/* The Podium */}
      {top3.length > 0 && (
        <div className="bg-gradient-to-b from-primary/10 to-transparent rounded-xl p-4 mb-8 pt-8 relative border border-outline-variant/30">
          <div className="flex items-end justify-center gap-2 h-40">
            {/* 2nd Place */}
            {top3[1] && (
              <div className="flex flex-col items-center w-1/3 relative z-10 transform translate-y-4">
                <div className="w-16 h-16 rounded-full border-4 border-[#C0C0C0] shadow-md overflow-hidden bg-surface-container mb-2 relative flex items-center justify-center font-bold text-surface-dim">
                  <span className="material-symbols-outlined text-[32px]">person</span>
                  <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-[#C0C0C0] rounded-full flex items-center justify-center text-white font-bold text-xs border-2 border-surface">2</div>
                </div>
                <span className="font-headline-md text-body-md text-on-surface truncate w-full text-center">{top3[1].nome.split(' ')[0]}</span>
                <span className="font-label-bold text-label-bold text-primary">{top3[1].pontos} pts</span>
              </div>
            )}

            {/* 1st Place */}
            {top3[0] && (
              <div className="flex flex-col items-center w-1/3 relative z-20 transform -translate-y-4">
                <div className="absolute -top-6 text-[#FFD700]">
                  <span className="material-symbols-outlined text-3xl" style={{fontVariationSettings: "'FILL' 1"}}>workspace_premium</span>
                </div>
                <div className="w-20 h-20 rounded-full border-4 border-[#FFD700] shadow-lg overflow-hidden bg-surface-container mb-2 relative flex items-center justify-center font-bold text-surface-dim">
                  <span className="material-symbols-outlined text-[40px]">person</span>
                  <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-[#FFD700] rounded-full flex items-center justify-center text-white font-bold text-xs border-2 border-surface">1</div>
                </div>
                <span className="font-headline-md text-headline-md text-on-surface truncate w-full text-center">{top3[0].nome.split(' ')[0]}</span>
                <span className="font-label-bold text-label-bold text-primary px-2 py-1 bg-primary/10 rounded-full mt-1">{top3[0].pontos} pts</span>
              </div>
            )}

            {/* 3rd Place */}
            {top3[2] && (
              <div className="flex flex-col items-center w-1/3 relative z-10 transform translate-y-6">
                <div className="w-14 h-14 rounded-full border-4 border-[#CD7F32] shadow-md overflow-hidden bg-surface-container mb-2 relative flex items-center justify-center font-bold text-surface-dim">
                  <span className="material-symbols-outlined text-[28px]">person</span>
                  <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-[#CD7F32] rounded-full flex items-center justify-center text-white font-bold text-xs border-2 border-surface">3</div>
                </div>
                <span className="font-headline-md text-body-sm text-on-surface truncate w-full text-center">{top3[2].nome.split(' ')[0]}</span>
                <span className="font-label-bold text-label-bold text-primary">{top3[2].pontos} pts</span>
              </div>
            )}
          </div>
          
          {/* Podium Base Decor */}
          <div className="absolute bottom-0 left-0 w-full flex justify-center opacity-20 pointer-events-none">
            <svg fill="none" height="40" viewBox="0 0 200 40" width="200" xmlns="http://www.w3.org/2000/svg">
              <path className="text-primary" d="M50 40L60 0H140L150 40H50Z" fill="currentColor"></path>
              <path className="text-[#C0C0C0]" d="M0 40L20 20H80L60 40H0Z" fill="currentColor"></path>
              <path className="text-[#CD7F32]" d="M200 40L180 25H120L140 40H200Z" fill="currentColor"></path>
            </svg>
          </div>
        </div>
      )}

      {/* The Table */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant overflow-hidden mb-8">
        <div className="flex items-center px-4 py-3 bg-surface-container-low border-b border-outline-variant">
          <div className="w-8 font-label-bold text-label-bold text-on-surface-variant">Pos</div>
          <div className="flex-1 font-label-bold text-label-bold text-on-surface-variant">Jogador</div>
          <div className="w-16 text-center font-label-bold text-label-bold text-on-surface-variant text-primary">Pts</div>
          <div className="w-16 text-center font-label-bold text-label-bold text-on-surface-variant text-primary">Média</div>
        </div>

        <div className="divide-y divide-outline-variant/50">
          {restOfRanking.map((jogador, index) => (
            <div key={jogador.id} className="flex items-center px-4 py-3 hover:bg-surface-bright transition-colors">
              <div className="w-8 font-headline-md text-body-md text-on-surface-variant">{index + 4}º</div>
              <div className="flex-1 flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-surface-variant flex items-center justify-center text-on-surface-variant text-xs font-bold">
                  {jogador.nome.charAt(0)}
                </div>
                <span className="font-headline-md text-body-md text-on-surface">{jogador.nome}</span>
              </div>
              <div className="w-16 text-center font-label-bold text-label-bold text-primary">{jogador.pontos}</div>
              <div className="w-16 text-center font-label-bold text-label-bold text-primary">{jogador.nota_galera_media ? jogador.nota_galera_media.toFixed(1) : '-'}</div>
            </div>
          ))}
          {restOfRanking.length === 0 && (
             <div className="py-6 text-center text-on-surface-variant text-sm">Sem mais jogadores no ranking.</div>
          )}
        </div>
      </div>
    </div>
  );
}
