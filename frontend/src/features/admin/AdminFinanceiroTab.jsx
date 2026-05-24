import React, { useState } from 'react';
import { useEvento } from '../../hooks/useEvento';

export function AdminFinanceiroTab() {
  const { evento } = useEvento(1);
  const [subTab, setSubTab] = useState('churrasco'); // 'mensalidades' | 'churrasco'

  const jogadoresConfirmados = evento?.presencas?.filter(p => p.vai_churrasco) || [];
  const cota = evento?.valor_churrasco || 40;
  const meta = 600; // Mock goal
  const arrecadado = jogadoresConfirmados.length * cota;
  const faltam = Math.max(0, meta - arrecadado);
  const progresso = Math.min(100, (arrecadado / meta) * 100);

  return (
    <div className="space-y-6 fade-in pb-8">
      {/* Sub-tabs */}
      <div className="flex p-1 bg-surface-container-low rounded-lg mb-4 shadow-inner">
        <button 
          onClick={() => setSubTab('mensalidades')}
          className={`flex-1 py-2 rounded-md font-label-bold text-label-bold transition-all ${subTab === 'mensalidades' ? 'bg-primary text-on-primary shadow-sm' : 'text-on-surface-variant hover:bg-surface-container'}`}
        >
          Mensalidades
        </button>
        <button 
          onClick={() => setSubTab('churrasco')}
          className={`flex-1 py-2 rounded-md font-label-bold text-label-bold transition-all ${subTab === 'churrasco' ? 'bg-primary text-on-primary shadow-sm' : 'text-on-surface-variant hover:bg-surface-container'}`}
        >
          Churrasco da Rodada
        </button>
      </div>

      {subTab === 'churrasco' ? (
        <>
          {/* Card Arrecadação */}
          <div className="rounded-xl p-5 shadow-ambient-1 relative overflow-hidden bg-gradient-to-br from-secondary-container to-barbecue-fire text-on-primary">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="font-headline-lg text-headline-lg font-bold">R$ {arrecadado.toFixed(2).replace('.', ',')}</h2>
                <p className="font-body-md text-on-primary/80">Arrecadado</p>
              </div>
              <div className="bg-white/20 px-3 py-1 rounded-full border border-white/30 backdrop-blur-sm text-sm font-label-bold text-label-bold">
                Cota: R$ {cota.toFixed(2).replace('.', ',')}
              </div>
            </div>

            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm font-label-bold text-label-bold">
                <span>Faltam: R$ {faltam.toFixed(2).replace('.', ',')}</span>
                <span>Meta: R$ {meta.toFixed(2).replace('.', ',')}</span>
              </div>
              <div className="w-full bg-white/20 rounded-full h-2 overflow-hidden">
                <div className="bg-white h-2 rounded-full transition-all duration-500" style={{ width: `${progresso}%` }}></div>
              </div>
            </div>

            <div className="text-right text-sm font-medium text-on-primary/90 mt-4">
              {jogadoresConfirmados.length} confirmados
            </div>
          </div>

          {/* Pagamentos List */}
          <div className="space-y-4">
            <h3 className="font-headline-md text-headline-md text-on-surface">Pagamentos</h3>
            <div className="glass-panel rounded-xl overflow-hidden shadow-ambient-1 divide-y divide-outline-variant/30">
              {jogadoresConfirmados.map((jogador, idx) => {
                const pago = idx % 2 === 0; // Mocking payment status
                return (
                  <div key={jogador.usuario_id} className="p-4 flex items-center justify-between bg-surface-container-lowest">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-surface-variant flex items-center justify-center text-on-surface-variant font-bold text-sm shrink-0">
                        {jogador.usuario_nome.charAt(0)}
                      </div>
                      <span className="font-headline-md text-[16px] text-on-surface">{jogador.usuario_nome}</span>
                    </div>
                    <button className={`px-4 py-2 rounded-lg font-label-bold text-label-bold border transition-colors ${pago ? 'bg-primary border-primary text-on-primary' : 'bg-transparent border-error text-error hover:bg-error/10'}`}>
                      {pago ? (
                        <span className="flex items-center gap-1"><span className="material-symbols-outlined text-[16px]">check</span> Pago</span>
                      ) : (
                        'Cobrar'
                      )}
                    </button>
                  </div>
                );
              })}
              {jogadoresConfirmados.length === 0 && (
                <div className="p-6 text-center text-tertiary">Nenhum confirmado para o churrasco ainda.</div>
              )}
            </div>
          </div>
        </>
      ) : (
        <div className="text-center py-10 bg-surface-container-low rounded-xl border border-outline-variant/30 shadow-inner">
          <span className="material-symbols-outlined text-[48px] text-tertiary mb-4">construction</span>
          <h3 className="font-headline-md text-on-surface mb-2">Mensalidades</h3>
          <p className="text-body-sm text-on-surface-variant px-4">Esta seção está em desenvolvimento.</p>
        </div>
      )}
    </div>
  );
}
