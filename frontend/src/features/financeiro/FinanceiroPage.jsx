import React, { useState, useEffect } from 'react';
import api from '../../services/api';

export function FinanceiroPage() {
  const [transacoes, setTransacoes] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFinanceiro = async () => {
      try {
        const response = await api.get('/financeiro/me');
        setTransacoes(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchFinanceiro();
  }, []);

  const saldo = transacoes?.reduce((acc, curr) => 
    curr.tipo === 'ENTRADA' ? acc + curr.valor : acc - curr.valor, 0
  ) || 0;

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-unit-3 p-4">
      {/* Page Header */}
      <div className="flex items-center gap-3 mb-2">
        <div className="w-10 h-10 rounded-full bg-primary-container/20 flex items-center justify-center text-primary">
          <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>account_balance_wallet</span>
        </div>
        <h2 className="font-headline-md text-headline-md text-on-surface">Meu Financeiro</h2>
      </div>

      {error && (
        <div className="p-3 bg-error-container text-on-error-container text-body-sm rounded-standard font-medium">
          Erro ao carregar dados do financeiro.
        </div>
      )}

      {/* Status da Mensalidade Card */}
      <section className="bg-surface-container-lowest rounded-xl p-4 shadow-sm border border-surface-variant/50 flex flex-col gap-4 relative overflow-hidden transition-all duration-300 hover:shadow-[0_4px_12px_rgba(0,110,47,0.08)] hover:-translate-y-[2px]">
        {/* Subtle indicator line */}
        <div className="absolute top-0 left-0 w-full h-1 bg-error"></div>
        <div className="flex justify-between items-start">
          <div>
            <h3 className="font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider mb-1">Mensalidade</h3>
            <p className="font-body-md text-body-md text-on-surface font-semibold">Maio/2026</p>
          </div>
          <div className="bg-error-container text-on-error-container px-3 py-1.5 rounded-full flex items-center gap-1">
            <span className="material-symbols-outlined text-[16px]">warning</span>
            <span className="font-label-bold text-label-bold">Pendente</span>
          </div>
        </div>
        <div className="flex items-end gap-2 mt-2">
          <span className="font-body-sm text-body-sm text-on-surface-variant">Valor:</span>
          <span className="font-headline-lg-mobile text-headline-lg-mobile text-on-surface font-extrabold tracking-tight">R$ 60,00</span>
        </div>
        <button className="mt-2 w-full bg-primary text-on-primary font-body-md text-body-md font-bold py-3 rounded-lg shadow-sm hover:bg-primary/90 active:scale-95 duration-100 flex items-center justify-center gap-2 transition-all">
          <span className="material-symbols-outlined text-[20px]">content_copy</span>
          Copiar Chave Pix do Admin
        </button>
      </section>

      {/* Caixa Extra (Transparência) */}
      <section className="bg-on-tertiary-fixed text-on-primary rounded-xl p-5 shadow-lg flex flex-col gap-5 relative overflow-hidden mt-2">
        {/* Decorative pattern/gradient */}
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary to-transparent pointer-events-none"></div>
        
        <div className="relative z-10 flex items-center gap-2 mb-1">
          <span className="material-symbols-outlined text-primary-fixed-dim">account_balance</span>
          <h3 className="font-label-bold text-label-bold uppercase tracking-wider text-tertiary-fixed-dim">Caixa da Pelada (Transparência)</h3>
        </div>
        
        <div className="relative z-10">
          <p className="font-body-sm text-body-sm text-tertiary-fixed-dim mb-1">Em caixa atual</p>
          <p className="font-display-lg text-display-lg font-extrabold text-on-primary">
            R$ {saldo.toFixed(2).replace('.', ',')}
          </p>
        </div>
        
        <div className="relative z-10 mt-2">
          <h4 className="font-label-bold text-label-bold text-tertiary-fixed-dim border-b border-white/10 pb-2 mb-3">Últimas Movimentações</h4>
          <ul className="flex flex-col gap-3">
            {transacoes?.length === 0 ? (
              <li className="text-sm text-tertiary-fixed-dim">Nenhuma movimentação registrada.</li>
            ) : (
              transacoes?.map(t => (
                <li key={t.id} className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                    t.tipo === 'ENTRADA' ? 'bg-primary-container/20 text-primary-fixed-dim' : 'bg-surface-variant/20 text-surface-dim'
                  }`}>
                    <span className="material-symbols-outlined text-[18px]">
                      {t.tipo === 'ENTRADA' ? 'arrow_downward' : 'arrow_upward'}
                    </span>
                  </div>
                  <div className="flex-1">
                    <p className="font-body-sm text-body-sm font-semibold text-on-primary">
                      {t.tipo === 'ENTRADA' ? '+' : '-'} R$ {t.valor.toFixed(2).replace('.', ',')}
                    </p>
                    <p className="font-label-bold text-label-bold text-tertiary-fixed-dim font-normal">{t.descricao}</p>
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>
      </section>
    </div>
  );
}
