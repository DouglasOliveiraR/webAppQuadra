import React from 'react';
import { useRanking } from '../../hooks/useRanking';
import { Trophy, Medal, AlertCircle } from 'lucide-react';
import { Card } from '../../components/ui/Card';

export function RankingPage() {
  const { ranking, loading, error } = useRanking();

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full pt-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center pt-20 text-error gap-4">
        <AlertCircle size={48} />
        <p>{error}</p>
      </div>
    );
  }

  const top3 = ranking.slice(0, 3);
  const rest = ranking.slice(3);

  return (
    <div className="flex flex-col gap-6 p-4 pt-8 pb-32">
      <header className="text-center">
        <Trophy className="mx-auto text-primary mb-2" size={40} />
        <h2 className="text-headline-md text-tertiary">Hall da Fama</h2>
        <h1 className="text-headline-lg-mobile text-on-background font-bold">Ranking Geral</h1>
      </header>

      {/* Podium Top 3 */}
      {top3.length > 0 && (
        <div className="flex justify-center items-end gap-2 mt-8 mb-4 h-48">
          {/* Segundo Colocado */}
          {top3[1] && (
            <div className="flex flex-col items-center w-1/3">
              <span className="text-sm font-bold text-on-background truncate w-full text-center">{top3[1].nome}</span>
              <span className="text-xs text-on-background/70 mb-2">{top3[1].pontos_ranking} pts</span>
              <div className="w-full bg-gradient-to-t from-surface-variant to-[#C0C0C0] h-24 rounded-t-lg flex justify-center pt-2 shadow-lg">
                <Medal className="text-white" size={24} />
              </div>
            </div>
          )}

          {/* Primeiro Colocado */}
          {top3[0] && (
            <div className="flex flex-col items-center w-1/3 z-10">
              <span className="text-base font-black text-primary truncate w-full text-center">{top3[0].nome}</span>
              <span className="text-sm text-primary mb-2 font-bold">{top3[0].pontos_ranking} pts</span>
              <div className="w-full bg-gradient-to-t from-primary/50 to-[#FFD700] h-32 rounded-t-lg flex justify-center pt-2 shadow-2xl">
                <Trophy className="text-white" size={32} />
              </div>
            </div>
          )}

          {/* Terceiro Colocado */}
          {top3[2] && (
            <div className="flex flex-col items-center w-1/3">
              <span className="text-sm font-bold text-on-background truncate w-full text-center">{top3[2].nome}</span>
              <span className="text-xs text-on-background/70 mb-2">{top3[2].pontos_ranking} pts</span>
              <div className="w-full bg-gradient-to-t from-surface-variant to-[#CD7F32] h-20 rounded-t-lg flex justify-center pt-2 shadow-lg">
                <Medal className="text-white" size={24} />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Restante da Lista */}
      <div className="flex flex-col gap-3">
        {rest.map((jogador, index) => (
          <Card key={jogador.id} variant="elevated" className="flex items-center p-4">
            <span className="font-bold text-lg text-tertiary/50 w-8">{index + 4}º</span>
            <div className="flex-1 ml-4">
              <h3 className="font-bold text-on-background">{jogador.nome}</h3>
              <p className="text-xs text-on-background/60">Nota da Galera: {jogador.nota_galera_media.toFixed(1)}</p>
            </div>
            <div className="font-black text-xl text-primary">{jogador.pontos_ranking}</div>
          </Card>
        ))}
      </div>
    </div>
  );
}
