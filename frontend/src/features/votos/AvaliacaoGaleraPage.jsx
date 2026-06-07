import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useEvento } from '../../hooks/useEvento';
import { showToast } from '../../components/ui/Toast';
import api from '../../services/api';

export function AvaliacaoGaleraPage() {
  const { evento, loading } = useEvento(1);
  const navigate = useNavigate();
  const [notas, setNotas] = useState({});

  const token = localStorage.getItem('token');
  let currentUserId = null;
  if (token) {
    try {
      const payloadBase64 = token.split('.')[1];
      const decodedPayload = JSON.parse(atob(payloadBase64));
      currentUserId = parseInt(decodedPayload.sub);
    } catch (e) {
      console.error(e);
    }
  }

  const candidatos = evento?.presencas?.filter(p => p.checkin_validado && p.usuario_id !== currentUserId) || [];

  const handleSliderChange = (id, value) => {
    setNotas(prev => ({ ...prev, [id]: parseInt(value, 10) }));
  };

  const handleSave = async () => {
    try {
      // Monta o payload garantindo que quem não teve o slider mexido receba a nota 5
      const notasPayload = {};
      candidatos.forEach(jogador => {
        notasPayload[jogador.usuario_id] = notas[jogador.usuario_id] !== undefined ? notas[jogador.usuario_id] : 5;
      });

      await api.post('/notas/galera', {
        evento_id: evento.id,
        notas: notasPayload
      });

      showToast('Avaliações salvas com sucesso!');
      navigate('/ranking');
    } catch (error) {
      console.error(error);
      showToast('Erro ao salvar as avaliações', 'error');
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-900">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary-fixed border-t-transparent"></div>
      </div>
    );
  }

  if (evento?.usuario_ja_avaliou) {
    return (
      <div className="flex flex-col items-center justify-center gap-6 p-6 h-screen text-center bg-gray-950 text-white -mt-20">
        <div className="w-20 h-20 bg-primary-fixed/20 rounded-full flex items-center justify-center shadow-lg border border-primary-fixed">
          <span className="material-symbols-outlined text-[40px] text-primary-fixed" style={{fontVariationSettings: "'FILL' 1"}}>check_circle</span>
        </div>
        <div className="space-y-2">
          <h2 className="font-headline-lg-mobile text-headline-lg-mobile font-bold text-white">Avaliação Concluída!</h2>
          <p className="font-body-md text-body-md text-gray-400 max-w-xs mx-auto">
            Suas notas para esta partida foram salvas com sucesso.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-gray-950 text-white -mt-20">
      <main className="flex-1 overflow-y-auto pt-24 px-container-margin-mobile pb-32">
        <div className="mb-8">
          <h2 className="font-headline-lg-mobile text-headline-lg-mobile text-on-primary mb-2 flex items-center gap-2">
            <span className="material-symbols-outlined text-primary-fixed">star</span>
            Avaliar Atuações
          </h2>
          <p className="font-body-md text-body-md text-gray-400">
            Arraste para dar a nota (0 a 10) para a galera que jogou hoje. Isso ajuda a equilibrar os times na próxima semana.
          </p>
        </div>

        <div className="space-y-4">
          {candidatos.map(jogador => {
            const nota = notas[jogador.usuario_id] !== undefined ? notas[jogador.usuario_id] : 5;
            return (
              <div key={jogador.usuario_id} className="bg-gray-900/80 border border-gray-800 rounded-xl p-4 shadow-ambient-1">
                <div className="flex justify-between items-center mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center text-gray-300 font-bold border border-gray-700">
                      {jogador.usuario_nome.charAt(0)}
                    </div>
                    <span className="font-headline-md text-[16px] text-white">{jogador.usuario_nome}</span>
                  </div>
                  <span className={`font-bold text-[18px] ${nota >= 7 ? 'text-primary-fixed' : nota >= 4 ? 'text-yellow-400' : 'text-red-400'}`}>
                    {nota}
                  </span>
                </div>
                
                <div className="relative px-2 pt-2 pb-1">
                  <div className="relative">
                    <input 
                      type="range" 
                      min="0" 
                      max="10" 
                      step="1" 
                      value={nota}
                      onChange={(e) => handleSliderChange(jogador.usuario_id, e.target.value)}
                      className="w-full h-3 rounded-full appearance-none cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-primary-fixed focus-visible:ring-offset-2 focus-visible:ring-offset-gray-900 shadow-inner"
                      style={{
                        background: `linear-gradient(to right, ${nota >= 7 ? '#6bff8f' : nota >= 4 ? '#facc15' : '#f87171'} ${(nota / 10) * 100}%, #374151 ${(nota / 10) * 100}%)`
                      }}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-gray-500 font-bold mt-2 px-1">
                    <span>0</span>
                    <span>5</span>
                    <span>10</span>
                  </div>
                </div>
              </div>
            );
          })}
          
          {candidatos.length === 0 && (
            <div className="text-center py-10 text-gray-500">
              Nenhum jogador para avaliar.
            </div>
          )}
        </div>
      </main>

      {/* Fixed Action Button */}
      <div className="fixed bottom-20 left-4 right-4 z-40 max-w-screen-xl mx-auto md:px-container-margin-desktop">
        <button 
          onClick={handleSave}
          className="w-full bg-primary-fixed text-on-primary-fixed font-headline-md text-[16px] font-bold py-4 px-6 rounded-xl shadow-[0_4px_20px_rgba(107,255,143,0.3)] flex items-center justify-center gap-2 hover:bg-inverse-primary transition-colors active:scale-95"
        >
          Salvar Notas e Ver Ranking
          <span className="material-symbols-outlined text-[20px]">save</span>
        </button>
      </div>
    </div>
  );
}
