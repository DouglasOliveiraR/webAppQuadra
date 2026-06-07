import React, { useState, useEffect } from 'react';
import api, { API_URL, getFotoUrl } from '../../services/api';
import { showToast } from '../../components/ui/Toast';

function PremioCard({ titulo, icone, subtitulo, pontos, estilo, vencedores }) {
  return (
    <div className={`bg-gradient-to-br ${estilo} border rounded-xl p-5 shadow-ambient-1 flex flex-col justify-between min-h-[160px] transition-all duration-300 hover:shadow-md hover:-translate-y-[2px]`}>
      <div>
        <div className="flex justify-between items-start mb-2">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[24px] icon-fill" aria-hidden="true">{icone}</span>
            <h4 className="font-headline-md text-headline-md font-bold">{titulo}</h4>
          </div>
          <span className="font-label-bold text-label-bold px-2 py-0.5 rounded-full bg-white/40 dark:bg-black/20 text-xs">
            {pontos} pts
          </span>
        </div>
        <p className="text-[12px] opacity-80 mb-4">{subtitulo}</p>
      </div>

      <div className="space-y-3">
        {vencedores && vencedores.length > 0 ? (
          vencedores.map(v => (
            <div key={v.id} className="flex items-center justify-between bg-white/50 dark:bg-black/10 rounded-lg p-2.5">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-surface-variant flex items-center justify-center text-on-surface-variant text-[11px] font-bold overflow-hidden shrink-0 border border-outline-variant/30">
                  {v.foto_url ? (
                    <img src={getFotoUrl(v.foto_url)} alt={v.nome} className="w-full h-full object-cover" />
                  ) : (
                    v.nome.charAt(0)
                  )}
                </div>
                <span className="font-body-md text-body-md font-bold text-on-surface">{v.nome}</span>
              </div>
              <span className="font-label-bold text-label-bold text-xs bg-white/80 dark:bg-black/20 px-2 py-1 rounded">
                {v.votos} {v.votos === 1 ? 'voto' : 'votos'}
              </span>
            </div>
          ))
        ) : (
          <div className="text-center py-3 text-body-sm opacity-60">Nenhum voto registrado.</div>
        )}
      </div>
    </div>
  );
}

export function RankingPage() {
  const [ranking, setRanking] = useState(null);
  const [ultimoResultado, setUltimoResultado] = useState(null);
  const [activeTab, setActiveTab] = useState('tabela'); // 'tabela' | 'ultimo'
  const [criterioOrdenacao, setCriterioOrdenacao] = useState('pontos'); // 'pontos' | 'nota'
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRanking = async () => {
    try {
      const response = await api.get('/ranking');
      setRanking(response.data);
    } catch (err) {
      setError(err);
    }
  };

  const fetchUltimoResultado = async () => {
    try {
      const response = await api.get('/ranking/ultimo-resultado');
      setUltimoResultado(response.data);
    } catch (err) {
      showToast('Erro ao carregar último resultado', 'error');
    }
  };

  useEffect(() => {
    const init = async () => {
      setIsLoading(true);
      await fetchRanking();
      await fetchUltimoResultado();
      setIsLoading(false);
    };
    init();
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

  // Obter o Top 3 para o Pódio ordenando dinamicamente
  const sortedRanking = ranking
    ? [...ranking].sort((a, b) => {
        if (criterioOrdenacao === 'pontos') {
          if (b.pontos_ranking !== a.pontos_ranking) {
            return b.pontos_ranking - a.pontos_ranking;
          }
          return (b.nota_galera_media || 0) - (a.nota_galera_media || 0);
        } else if (criterioOrdenacao === 'nota') {
          if (b.nota_galera_media !== a.nota_galera_media) {
            return (b.nota_galera_media || 0) - (a.nota_galera_media || 0);
          }
          return b.pontos_ranking - a.pontos_ranking;
        } else if (criterioOrdenacao === 'gols') {
          if (b.gols_total !== a.gols_total) {
            return (b.gols_total || 0) - (a.gols_total || 0);
          }
          return b.pontos_ranking - a.pontos_ranking;
        }
        return 0;
      })
    : [];
  const top3 = sortedRanking.slice(0, 3);
  const restOfRanking = sortedRanking.slice(3);

  return (
    <div className="flex flex-col w-full pb-6">
      {/* Título da tela */}
      <div className="flex items-center gap-3 mb-6 mt-4">
        <div className="w-10 h-10 rounded-full flex items-center justify-center shadow-sm bg-primary-container text-on-primary-container">
          <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}} aria-hidden="true">trophy</span>
        </div>
        <h2 className="font-headline-md text-headline-md text-on-surface">Resenha & Ranking</h2>
      </div>

      {/* Tabs */}
      <div className="flex p-1 bg-surface-container-low rounded-lg mb-8 shadow-inner" role="tablist">
        <button 
          onClick={() => setActiveTab('tabela')}
          role="tab"
          aria-selected={activeTab === 'tabela'}
          className={`flex-1 py-2 rounded-md font-label-bold text-label-bold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
            activeTab === 'tabela' ? 'bg-surface text-primary shadow-sm' : 'text-on-surface-variant hover:bg-surface-container'
          }`}
        >
          Tabela Geral
        </button>
        <button 
          onClick={() => setActiveTab('ultimo')}
          role="tab"
          aria-selected={activeTab === 'ultimo'}
          className={`flex-1 py-2 rounded-md font-label-bold text-label-bold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
            activeTab === 'ultimo' ? 'bg-surface text-primary shadow-sm' : 'text-on-surface-variant hover:bg-surface-container'
          }`}
        >
          Último Jogo
        </button>
      </div>

      {/* Guia Tabela Geral */}
      {activeTab === 'tabela' && (
        <div className="space-y-6 animate-fade-in">
          {/* Seletor de Critério de Ordenação */}
          <div className="flex items-center justify-between bg-surface-container-low px-4 py-2.5 rounded-xl border border-outline-variant/20 mb-2">
            <span className="font-label-bold text-label-bold text-on-surface-variant uppercase text-[11px] tracking-wider">Classificar por</span>
            <div className="flex gap-2" role="group">
              <button 
                onClick={() => setCriterioOrdenacao('pontos')}
                aria-pressed={criterioOrdenacao === 'pontos'}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
                  criterioOrdenacao === 'pontos' 
                    ? 'bg-primary text-on-primary shadow-sm' 
                    : 'bg-surface-variant text-on-surface-variant hover:bg-surface-container-high'
                }`}
              >
                Pontos
              </button>
              <button 
                onClick={() => setCriterioOrdenacao('nota')}
                aria-pressed={criterioOrdenacao === 'nota'}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
                  criterioOrdenacao === 'nota' 
                    ? 'bg-primary text-on-primary shadow-sm' 
                    : 'bg-surface-variant text-on-surface-variant hover:bg-surface-container-high'
                }`}
              >
                Média da Galera
              </button>
              <button 
                onClick={() => setCriterioOrdenacao('gols')}
                aria-pressed={criterioOrdenacao === 'gols'}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
                  criterioOrdenacao === 'gols' 
                    ? 'bg-primary text-on-primary shadow-sm' 
                    : 'bg-surface-variant text-on-surface-variant hover:bg-surface-container-high'
                }`}
              >
                Gols
              </button>
            </div>
          </div>

          {/* O Pódio */}
          {top3.length > 0 && (
            <div className="bg-gradient-to-b from-primary/10 to-transparent rounded-xl p-4 pt-8 relative border border-outline-variant/30">
              <div className="flex items-end justify-center gap-2 h-40">
                {/* 2º Lugar */}
                {top3[1] && (
                  <div className="flex flex-col items-center w-1/3 relative z-10 transform translate-y-4">
                    <div className="w-16 h-16 rounded-full border-4 border-[#C0C0C0] shadow-md overflow-hidden bg-surface-container mb-2 relative flex items-center justify-center font-bold text-surface-dim">
                      {top3[1].foto_url ? (
                        <img src={getFotoUrl(top3[1].foto_url)} alt={top3[1].nome} className="w-full h-full object-cover" />
                      ) : (
                        <span className="material-symbols-outlined text-[32px]" aria-hidden="true">person</span>
                      )}
                      <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-[#C0C0C0] rounded-full flex items-center justify-center text-white font-bold text-xs border-2 border-surface">
                        <span aria-hidden="true">2</span>
                        <span className="sr-only">2º Lugar</span>
                      </div>
                    </div>
                    <span className="font-headline-md text-body-md text-on-surface truncate w-full text-center">{top3[1].nome.split(' ')[0]}</span>
                    <span className="font-label-bold text-label-bold text-primary">
                      {criterioOrdenacao === 'pontos' 
                        ? `${top3[1].pontos_ranking} pts` 
                        : criterioOrdenacao === 'nota'
                        ? `${top3[1].nota_galera_media ? top3[1].nota_galera_media.toFixed(1) : '-'} ★`
                        : `${top3[1].gols_total || 0} gols`}
                    </span>
                  </div>
                )}

                {/* 1º Lugar */}
                {top3[0] && (
                  <div className="flex flex-col items-center w-1/3 relative z-20 transform -translate-y-4">
                    <div className="absolute -top-6 text-[#FFD700]">
                      <span className="material-symbols-outlined text-3xl" style={{fontVariationSettings: "'FILL' 1"}} aria-hidden="true">workspace_premium</span>
                    </div>
                    <div className="w-20 h-20 rounded-full border-4 border-[#FFD700] shadow-lg overflow-hidden bg-surface-container mb-2 relative flex items-center justify-center font-bold text-surface-dim">
                      {top3[0].foto_url ? (
                        <img src={getFotoUrl(top3[0].foto_url)} alt={top3[0].nome} className="w-full h-full object-cover" />
                      ) : (
                        <span className="material-symbols-outlined text-[40px]" aria-hidden="true">person</span>
                      )}
                      <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-[#FFD700] rounded-full flex items-center justify-center text-white font-bold text-xs border-2 border-surface">
                        <span aria-hidden="true">1</span>
                        <span className="sr-only">1º Lugar</span>
                      </div>
                    </div>
                    <span className="font-headline-md text-headline-md text-on-surface truncate w-full text-center">{top3[0].nome.split(' ')[0]}</span>
                    <span className="font-label-bold text-label-bold text-primary px-2 py-1 bg-primary/10 rounded-full mt-1">
                      {criterioOrdenacao === 'pontos' 
                        ? `${top3[0].pontos_ranking} pts` 
                        : criterioOrdenacao === 'nota'
                        ? `${top3[0].nota_galera_media ? top3[0].nota_galera_media.toFixed(1) : '-'} ★`
                        : `${top3[0].gols_total || 0} gols`}
                    </span>
                  </div>
                )}

                {/* 3º Lugar */}
                {top3[2] && (
                  <div className="flex flex-col items-center w-1/3 relative z-10 transform translate-y-6">
                    <div className="w-14 h-14 rounded-full border-4 border-[#CD7F32] shadow-md overflow-hidden bg-surface-container mb-2 relative flex items-center justify-center font-bold text-surface-dim">
                      {top3[2].foto_url ? (
                        <img src={getFotoUrl(top3[2].foto_url)} alt={top3[2].nome} className="w-full h-full object-cover" />
                      ) : (
                        <span className="material-symbols-outlined text-[28px]" aria-hidden="true">person</span>
                      )}
                      <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-[#CD7F32] rounded-full flex items-center justify-center text-white font-bold text-xs border-2 border-surface">
                        <span aria-hidden="true">3</span>
                        <span className="sr-only">3º Lugar</span>
                      </div>
                    </div>
                    <span className="font-headline-md text-body-sm text-on-surface truncate w-full text-center">{top3[2].nome.split(' ')[0]}</span>
                    <span className="font-label-bold text-label-bold text-primary">
                      {criterioOrdenacao === 'pontos' 
                        ? `${top3[2].pontos_ranking} pts` 
                        : criterioOrdenacao === 'nota'
                        ? `${top3[2].nota_galera_media ? top3[2].nota_galera_media.toFixed(1) : '-'} ★`
                        : `${top3[2].gols_total || 0} gols`}
                    </span>
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

          {/* Tabela de Classificação */}
          <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant overflow-hidden">
            <div className="flex items-center px-4 py-3 bg-surface-container-low border-b border-outline-variant">
              <div className="w-8 font-label-bold text-label-bold text-on-surface-variant">Pos</div>
              <div className="flex-1 font-label-bold text-label-bold text-on-surface-variant">Jogador</div>
              <div className={`w-16 text-center font-label-bold text-label-bold ${criterioOrdenacao === 'pontos' ? 'text-primary font-bold' : 'text-on-surface-variant'}`}>Pts</div>
              <div className={`w-16 text-center font-label-bold text-label-bold ${criterioOrdenacao === 'nota' ? 'text-primary font-bold' : 'text-on-surface-variant'}`}>Média</div>
              <div className={`w-12 text-center font-label-bold text-label-bold ${criterioOrdenacao === 'gols' ? 'text-primary font-bold' : 'text-on-surface-variant'}`}>Gols</div>
            </div>

            <div className="divide-y divide-outline-variant/50">
              {restOfRanking.map((jogador, index) => (
                <div key={jogador.id} className="flex items-center px-4 py-3 hover:bg-surface-container hover:shadow-sm hover:-translate-y-[1px] transition-all duration-200">
                  <div className="w-8 font-headline-md text-body-md text-on-surface-variant">{index + 4}º</div>
                  <div className="flex-1 flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-surface-variant flex items-center justify-center text-on-surface-variant text-xs font-bold overflow-hidden">
                      {jogador.foto_url ? (
                        <img src={getFotoUrl(jogador.foto_url)} alt={jogador.nome} className="w-full h-full object-cover" />
                      ) : (
                        jogador.nome.charAt(0)
                      )}
                    </div>
                    <div className="flex flex-col">
                      <span className="font-headline-md text-body-md text-on-surface">{jogador.nome}</span>
                      {jogador.premios && jogador.premios.length > 0 && (
                        <div className="flex gap-1 mt-0.5 flex-wrap">
                          {jogador.premios.map(p => {
                            let bg = 'bg-surface-variant text-on-surface-variant border-outline-variant/30';
                            let icon = 'star';
                            if(p.categoria === 'BOLA_CHEIA') { bg = 'bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400 dark:border-amber-700'; icon = 'emoji_events'; }
                            if(p.categoria === 'GOL_BONITO') { bg = 'bg-emerald-100 text-emerald-800 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-400 dark:border-emerald-700'; icon = 'sports_soccer'; }
                            if(p.categoria === 'BOLA_MURCHA') { bg = 'bg-rose-100 text-rose-800 border-rose-200 dark:bg-rose-900/30 dark:text-rose-400 dark:border-rose-700'; icon = 'thumb_down'; }
                            if(p.categoria === 'LAFON') { bg = 'bg-pink-100 text-pink-800 border-pink-200 dark:bg-pink-900/30 dark:text-pink-400 dark:border-pink-700'; icon = 'sentiment_very_dissatisfied'; }
                            
                            return (
                              <div key={p.categoria} className={`flex items-center gap-0.5 px-1 py-0.5 rounded text-[10px] font-bold border ${bg}`}>
                                <span className="material-symbols-outlined text-[10px]">{icon}</span>
                                <span>{p.quantidade}x</span>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className={`w-16 text-center text-sm ${criterioOrdenacao === 'pontos' ? 'font-bold text-primary' : 'font-medium text-on-surface'}`}>
                    {jogador.pontos_ranking}
                  </div>
                  <div className={`w-16 text-center text-sm ${criterioOrdenacao === 'nota' ? 'font-bold text-primary' : 'font-medium text-on-surface-variant'}`}>
                    {jogador.nota_galera_media ? jogador.nota_galera_media.toFixed(1) : '-'}
                  </div>
                  <div className={`w-12 text-center text-sm ${criterioOrdenacao === 'gols' ? 'font-bold text-primary' : 'font-medium text-on-surface-variant'}`}>
                    {jogador.gols_total || 0}
                  </div>
                </div>
              ))}
              {restOfRanking.length === 0 && (
                 <div className="py-6 text-center text-on-surface-variant text-sm">Sem mais jogadores no ranking.</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Guia Último Jogo */}
      {activeTab === 'ultimo' && (
        <div className="space-y-6 animate-fade-in">
          {(!ultimoResultado || ultimoResultado.detail) ? (
            <div className="py-12 text-center text-on-surface-variant bg-surface-container-lowest rounded-xl shadow-ambient-1 border border-outline-variant/30">
              <span className="material-symbols-outlined text-[48px] text-tertiary mb-3">sports_soccer</span>
              <p className="font-body-md text-body-md">Nenhuma pelada finalizada com votação apurada ainda.</p>
            </div>
          ) : (
            <>
              {/* Info Geral do Evento */}
              <div className="bg-surface-container-lowest border border-outline-variant/30 rounded-xl p-4 shadow-ambient-1 flex flex-col gap-2">
                <span className="font-label-bold text-label-bold text-primary uppercase text-[11px] tracking-wider">Última Partida Finalizada</span>
                <div className="flex items-center gap-2 text-on-surface">
                  <span className="material-symbols-outlined text-[20px] text-tertiary">calendar_today</span>
                  <span className="font-body-md text-body-md font-bold">
                    {(() => {
                      try {
                        const partes = ultimoResultado.data_jogo.split('-');
                        return `${partes[2]}/${partes[1]}/${partes[0]}`;
                      } catch (e) {
                        return ultimoResultado.data_jogo;
                      }
                    })()}
                  </span>
                </div>
                {ultimoResultado.endereco && (
                  <div className="flex items-center gap-2 text-on-surface-variant text-[14px]">
                    <span className="material-symbols-outlined text-[20px]">location_on</span>
                    <span>{ultimoResultado.endereco}</span>
                  </div>
                )}
              </div>

              {/* Grid de Prêmios */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Bola Cheia */}
                <PremioCard 
                  titulo="Bola Cheia"
                  icone="emoji_events"
                  subtitulo="O craque da rodada"
                  pontos="+3"
                  estilo="from-[#FFFBEB] to-[#FEF3C7] dark:from-amber-950/20 dark:to-amber-900/10 border-amber-200/50 text-[#D97706] dark:text-amber-400"
                  vencedores={ultimoResultado.vencedores?.BOLA_CHEIA}
                />

                {/* Gol Bonito */}
                <PremioCard 
                  titulo="Gol Bonito"
                  icone="sports_soccer"
                  subtitulo="A pintura do dia"
                  pontos="+2"
                  estilo="from-[#F0FDF4] to-[#DCFCE7] dark:from-emerald-950/20 dark:to-emerald-900/10 border-emerald-200/50 text-[#059669] dark:text-emerald-400"
                  vencedores={ultimoResultado.vencedores?.GOL_BONITO}
                />

                {/* Bola Murcha */}
                <PremioCard 
                  titulo="Bola Murcha"
                  icone="thumb_down"
                  subtitulo="Deixou a desejar"
                  pontos="-1"
                  estilo="from-[#FEF2F2] to-[#FEE2E2] dark:from-rose-950/20 dark:to-rose-900/10 border-rose-200/50 text-[#DC2626] dark:text-rose-400"
                  vencedores={ultimoResultado.vencedores?.BOLA_MURCHA}
                />

                {/* Lafon */}
                <PremioCard 
                  titulo="O Lafon"
                  icone="sentiment_very_dissatisfied"
                  subtitulo="O chorão da rodada"
                  pontos="-1"
                  estilo="from-[#FDF2F8] to-[#FCE7F3] dark:from-pink-950/20 dark:to-pink-900/10 border-pink-200/50 text-[#DB2777] dark:text-pink-400"
                  vencedores={ultimoResultado.vencedores?.LAFON}
                />
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
