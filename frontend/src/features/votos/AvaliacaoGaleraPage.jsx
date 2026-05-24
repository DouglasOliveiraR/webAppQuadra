import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useEvento } from '../../hooks/useEvento';
import { showToast } from '../../components/ui/Toast';

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
    setNotas(prev => ({ ...prev, [id]: parseFloat(value) }));
  };

  const handleSave = () => {
    // API call to save notas
    showToast('Avaliações salvas com sucesso!');
    navigate('/ranking');
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-900">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary-fixed border-t-transparent"></div>
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
            const nota = notas[jogador.usuario_id] || 5.0;
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
                    {nota.toFixed(1)}
                  </span>
                </div>
                
                <div className="relative px-2">
                  <input 
                    type="range" 
                    min="0" 
                    max="10" 
                    step="0.1" 
                    value={nota}
                    onChange={(e) => handleSliderChange(jogador.usuario_id, e.target.value)}
                    className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer"
                    style={{
                      background: `linear-gradient(to right, var(--color-primary-fixed) ${(nota / 10) * 100}%, #1f2937 ${(nota / 10) * 100}%)`
                    }}
                  />
                  {/* Custom CSS for webkit thumb is usually global, but inline styling works for track */}
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
      <style dangerouslySetInnerHTML={{__html: `
        input[type=range]::-webkit-slider-thumb {
          -webkit-appearance: none;
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: var(--color-primary-fixed);
          cursor: pointer;
          margin-top: -9px;
          box-shadow: 0 0 10px rgba(107,255,143,0.5);
        }
      `}} />
    </div>
  );
}
