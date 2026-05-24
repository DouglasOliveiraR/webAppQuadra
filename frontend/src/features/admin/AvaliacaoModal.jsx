import React, { useState } from 'react';

export function AvaliacaoModal({ isOpen, onClose, jogador, onSave }) {
  const [nota, setNota] = useState(7.5);

  if (!isOpen || !jogador) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4 fade-in">
      <div className="bg-surface w-full max-w-sm rounded-3xl p-6 shadow-ambient-2 relative slide-up">
        
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="font-headline-md text-headline-md text-on-surface font-bold">Nota Técnica (Admin)</h2>
          <button onClick={onClose} className="w-8 h-8 rounded-full bg-surface-container-low flex items-center justify-center text-on-surface-variant hover:bg-surface-variant transition-colors">
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Player Info */}
        <div className="bg-surface-container-low rounded-xl p-3 flex items-center gap-4 mb-8">
          <div className="w-12 h-12 rounded-full bg-surface-variant flex items-center justify-center text-on-surface-variant font-bold text-lg shrink-0">
            {jogador.nome.charAt(0)}
          </div>
          <div>
            <h3 className="font-headline-md text-[18px] text-on-surface">{jogador.nome}</h3>
            <p className="text-sm text-tertiary">{jogador.posicao}</p>
          </div>
        </div>

        {/* Rating Value */}
        <div className="text-center mb-6">
          <span className="text-[64px] font-bold text-primary leading-none tracking-tighter">
            {nota.toFixed(1)}
          </span>
        </div>

        {/* Slider */}
        <div className="mb-8 relative px-2">
          <input 
            type="range" 
            min="0" 
            max="10" 
            step="0.1" 
            value={nota}
            onChange={(e) => setNota(parseFloat(e.target.value))}
            className="w-full h-2 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-primary"
            style={{
              background: `linear-gradient(to right, var(--color-primary) ${(nota / 10) * 100}%, var(--color-surface-variant) ${(nota / 10) * 100}%)`
            }}
          />
          <div className="flex justify-between text-xs font-label-bold text-on-surface-variant mt-2 font-bold">
            <span>0</span>
            <span>10</span>
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-surface-container-low rounded-xl p-4 mb-8 flex gap-3 text-on-surface-variant text-[13px] leading-relaxed">
          <span className="material-symbols-outlined text-[20px] shrink-0 text-tertiary">info</span>
          <p>
            Atenção: Esta nota é secreta. Ela só será usada nos bastidores para balancear os times caso você escolha a opção 'Usar Minha Nota' no sorteio.
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button 
            onClick={onClose}
            className="flex-1 py-3 border border-outline text-on-surface rounded-xl font-label-bold text-label-bold hover:bg-surface-container transition-colors"
          >
            Cancelar
          </button>
          <button 
            onClick={() => { onSave(jogador.id, nota); onClose(); }}
            className="flex-1 py-3 bg-primary text-on-primary rounded-xl font-label-bold text-label-bold shadow-md hover:bg-primary/90 transition-colors flex items-center justify-center gap-2"
          >
            <span className="material-symbols-outlined text-[18px]">lock</span>
            Salvar Nota
          </button>
        </div>

      </div>
    </div>
  );
}
