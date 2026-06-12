import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { showToast } from '../../components/ui/Toast';

export function FinanceiroPage() {
  const [transacoes, setTransacoes] = useState(null);
  const [transparencia, setTransparencia] = useState(null);
  const [eventos, setEventos] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const getMesAtual = () => {
    const hoje = new Date();
    const ano = hoje.getFullYear();
    const mes = String(hoje.getMonth() + 1).padStart(2, '0');
    return `${ano}-${mes}`;
  };

  const [selectedMonth, setSelectedMonth] = useState(getMesAtual());

  useEffect(() => {
    const fetchFinanceiro = async () => {
      try {
        setIsLoading(true);
        const [respMe, respTransp] = await Promise.all([
          api.get('/financeiro/me', { params: { mes: selectedMonth } }),
          api.get('/financeiro/transparencia', { params: { mes: selectedMonth } })
        ]);
        setTransacoes(respMe.data);
        setTransparencia(respTransp.data);
      } catch (err) {
        setError(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchFinanceiro();
  }, [selectedMonth]);

  useEffect(() => {
    const fetchEventos = async () => {
      try {
        const response = await api.get('/eventos');
        setEventos(response.data || []);
      } catch (err) {
        console.error("Erro ao buscar eventos:", err);
      }
    };
    fetchEventos();
  }, []);

  // Filtra eventos do mês selecionado
  const eventosDoMes = eventos?.filter(e => e.data_jogo && e.data_jogo.startsWith(selectedMonth)) || [];
  const eventoDoMes = eventosDoMes.length > 0 
    ? eventosDoMes.sort((a, b) => b.id - a.id)[0]
    : (eventos.length > 0 ? eventos.sort((a, b) => b.id - a.id)[0] : null);

  // Procurar se existe registro de MENSALIDADE nas transações do usuário logado para o mês selecionado
  const mensalidade = transacoes?.find(t => t.tipo === 'MENSALIDADE' && t.mes_referencia === selectedMonth);
  const temMensalidade = !!mensalidade;
  const isPago = temMensalidade ? mensalidade.status_pagamento === 'PAGO' : false;

  const valorMensalidade = temMensalidade 
    ? mensalidade.valor 
    : (eventoDoMes?.valor_mensalidade !== undefined && eventoDoMes?.valor_mensalidade !== null ? eventoDoMes.valor_mensalidade : 60.00);

  const transacaoChurrasco = transacoes?.find(t => t.tipo.startsWith('CHURRASCO') && t.mes_referencia === selectedMonth);
  const temChurrasco = !!transacaoChurrasco || eventoDoMes?.flag_churrasco;
  const isChurrascoPago = transacaoChurrasco ? transacaoChurrasco.status_pagamento === 'PAGO' : false;
  const valorChurrasco = transacaoChurrasco ? transacaoChurrasco.valor : (eventoDoMes?.valor_churrasco || 0);

  const saldo = transparencia ? transparencia.saldo : 0;
  const arrecadadoChurrasco = transparencia?.arrecadado_churrasco || 0;

  const formatarSaldo = (valor) => {
    const absoluto = Math.abs(valor).toFixed(2).replace('.', ',');
    return valor < 0 ? `- R$ ${absoluto}` : `R$ ${absoluto}`;
  };

  const formatarMesAno = (mesStr) => {
    if (!mesStr) return 'Mensalidade';
    try {
      // Ex: "2026-05" -> Ano e Mês
      const parts = mesStr.split('-');
      const data = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, 1);
      return data.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })
        .replace(/^\w/, (c) => c.toUpperCase());
    } catch (e) {
      return 'Mensalidade';
    }
  };

  const handleCopiarPix = () => {
    if (eventoDoMes?.chave_pix) {
      navigator.clipboard.writeText(eventoDoMes.chave_pix);
      showToast('Chave Pix copiada com sucesso!');
    } else {
      showToast('Nenhuma chave Pix cadastrada pelo Admin.', 'error');
    }
  };

  const mesesOpcoes = [
    { value: "2026-01", label: "Janeiro / 2026" },
    { value: "2026-02", label: "Fevereiro / 2026" },
    { value: "2026-03", label: "Março / 2026" },
    { value: "2026-04", label: "Abril / 2026" },
    { value: "2026-05", label: "Maio / 2026" },
    { value: "2026-06", label: "Junho / 2026" },
    { value: "2026-07", label: "Julho / 2026" },
    { value: "2026-08", label: "Agosto / 2026" },
    { value: "2026-09", label: "Setembro / 2026" },
    { value: "2026-10", label: "Outubro / 2026" },
    { value: "2026-11", label: "Novembro / 2026" },
    { value: "2026-12", label: "Dezembro / 2026" }
  ];

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary border-t-transparent"></div>
      </div>
    );
  }

  // Filtra as transações correspondentes ao mês de referência selecionado para as movimentações
  // Remove itens de CHURRASCO da visão pública de finanças conforme solicitado
  const transacoesFiltradas = transacoes?.filter(
    t => t.mes_referencia === selectedMonth && !t.tipo.startsWith('CHURRASCO')
  ) || [];

  return (
    <div className="flex flex-col gap-unit-3 p-4">
      {/* Page Header com Seletor de Mês */}
      <div className="flex justify-between items-center flex-wrap gap-3 mb-2">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary-container/20 flex items-center justify-center text-primary">
            <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>account_balance_wallet</span>
          </div>
          <h2 className="font-headline-md text-headline-md text-on-surface">Meu Financeiro</h2>
        </div>
        
        <select 
          value={selectedMonth}
          onChange={(e) => setSelectedMonth(e.target.value)}
          className="bg-surface-container-high border-2 border-outline-variant/30 text-on-surface text-sm rounded-lg px-3 py-2 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all font-body-md"
        >
          {mesesOpcoes.map(m => (
            <option key={m.value} value={m.value} className="bg-surface text-on-surface">{m.label}</option>
          ))}
        </select>
      </div>

      {error && (
        <div className="p-3 bg-error-container text-on-error-container text-body-sm rounded-standard font-medium">
          Erro ao carregar dados do financeiro.
        </div>
      )}

      {/* Status da Mensalidade Card */}
      {(temMensalidade || (eventoDoMes && !isLoading)) && (
        <section className="bento-card p-5 bg-surface border border-outline/10 flex flex-col gap-4 relative overflow-hidden transition-all duration-300 hover:shadow-ambient-2 hover:-translate-y-[2px]">
          {/* Subtle indicator line */}
          <div className={`absolute top-0 left-0 w-full h-1 ${isPago ? 'bg-primary' : 'bg-error'}`}></div>
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider mb-1">Mensalidade</h3>
              <p className="font-body-md text-body-md text-on-surface font-bold">{formatarMesAno(selectedMonth)}</p>
            </div>
            <div className={`${isPago ? 'bg-primary/10 text-primary' : 'bg-error/10 text-error'} px-3 py-1.5 rounded-full flex items-center gap-1 border ${isPago ? 'border-primary/20' : 'border-error/20'}`}>
              <span className="material-symbols-outlined text-[16px]">{isPago ? 'check_circle' : 'warning'}</span>
              <span className="font-label-bold text-label-bold">{isPago ? 'Pago' : 'Pendente'}</span>
            </div>
          </div>
          <div className="flex items-end gap-2 mt-2">
            <span className="font-body-sm text-body-sm text-on-surface-variant">Valor:</span>
            <span className="font-headline-lg-mobile text-headline-lg-mobile text-on-surface font-extrabold tracking-tight">R$ {valorMensalidade.toFixed(2).replace('.', ',')}</span>
          </div>
          {!isPago && (
            <button 
              onClick={handleCopiarPix}
              className="mt-2 w-full bg-primary text-on-primary font-body-md text-body-md font-bold py-3 rounded-lg shadow-sm hover:bg-primary/90 active:scale-95 duration-100 flex items-center justify-center gap-2 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
            >
              <span className="material-symbols-outlined text-[20px]" aria-hidden="true">content_copy</span>
              Copiar Chave Pix do Admin
            </button>
          )}
        </section>
      )}

      {/* Status do Churrasco Card */}
      {temChurrasco && (
        <section className="bento-card p-5 bg-surface border border-outline/10 flex flex-col gap-4 relative overflow-hidden transition-all duration-300 hover:shadow-ambient-2 hover:-translate-y-[2px] mt-2">
          {/* Subtle indicator line */}
          <div className={`absolute top-0 left-0 w-full h-1 ${isChurrascoPago ? 'bg-primary' : 'bg-error'}`}></div>
          <div className="flex justify-between items-start">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="material-symbols-outlined text-on-surface-variant text-[18px]">outdoor_grill</span>
                <h3 className="font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider">Churrasco</h3>
              </div>
              <p className="font-body-md text-body-md text-on-surface font-bold">{formatarMesAno(selectedMonth)}</p>
            </div>
            <div className={`${isChurrascoPago ? 'bg-primary/10 text-primary' : 'bg-error/10 text-error'} px-3 py-1.5 rounded-full flex items-center gap-1 border ${isChurrascoPago ? 'border-primary/20' : 'border-error/20'}`}>
              <span className="material-symbols-outlined text-[16px]">{isChurrascoPago ? 'check_circle' : 'warning'}</span>
              <span className="font-label-bold text-label-bold">{isChurrascoPago ? 'Pago' : 'Pendente'}</span>
            </div>
          </div>
          <div className="flex items-end gap-2 mt-2">
            <span className="font-body-sm text-body-sm text-on-surface-variant">Valor:</span>
            <span className="font-headline-lg-mobile text-headline-lg-mobile text-on-surface font-extrabold tracking-tight">R$ {valorChurrasco.toFixed(2).replace('.', ',')}</span>
          </div>
          {!isChurrascoPago && (
            <button 
              onClick={handleCopiarPix}
              className="mt-2 w-full bg-primary text-on-primary font-body-md text-body-md font-bold py-3 rounded-lg shadow-sm hover:bg-primary/90 active:scale-95 duration-100 flex items-center justify-center gap-2 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
            >
              <span className="material-symbols-outlined text-[20px]" aria-hidden="true">content_copy</span>
              Copiar Chave Pix do Admin
            </button>
          )}
        </section>
      )}

      {/* Transparência do Churrasco */}
      {arrecadadoChurrasco > 0 && (
        <section className="rounded-3xl shadow-bento border border-outline/10 p-6 bg-tertiary text-on-tertiary flex flex-col gap-4 relative overflow-hidden mt-2">
          <div className="absolute inset-0 opacity-20 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-white to-transparent pointer-events-none"></div>
          
          <div className="relative z-10 flex items-center gap-2 mb-1">
            <span className="material-symbols-outlined text-white/90">outdoor_grill</span>
            <h3 className="font-label-bold text-label-bold uppercase tracking-wider text-white/90">Caixa do Churrasco (Transparência)</h3>
          </div>
          
          <div className="relative z-10">
            <p className="font-body-sm text-body-sm text-white/80 mb-1">Total arrecadado</p>
            <p className="font-display-lg text-display-lg font-extrabold text-white">
              {formatarSaldo(arrecadadoChurrasco).replace('-', '')}
            </p>
          </div>
        </section>
      )}

      {/* Caixa Extra (Transparência) */}
      <section className="rounded-3xl shadow-bento border border-outline/10 p-6 bg-primary text-on-primary flex flex-col gap-5 relative overflow-hidden mt-2">
        {/* Decorative pattern/gradient */}
        <div className="absolute inset-0 opacity-20 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-white to-transparent pointer-events-none"></div>
        
        <div className="relative z-10 flex items-center gap-2 mb-1">
          <span className="material-symbols-outlined text-white/90">account_balance</span>
          <h3 className="font-label-bold text-label-bold uppercase tracking-wider text-white/90">Caixa da Pelada (Transparência)</h3>
        </div>
        
        <div className="relative z-10">
          <p className="font-body-sm text-body-sm text-white/80 mb-1">Em caixa atual</p>
          <p className={`font-display-lg text-display-lg font-extrabold ${saldo < 0 ? 'text-[#FCA5A5]' : 'text-white'}`}>
            {formatarSaldo(saldo)}
          </p>
        </div>
        
        <div className="relative z-10 mt-2">
          <h4 className="font-label-bold text-label-bold text-white/80 border-b border-white/20 pb-2 mb-3">Movimentações de {formatarMesAno(selectedMonth)}</h4>
          <ul className="flex flex-col gap-3">
            {transacoesFiltradas.length === 0 ? (
              <li className="text-sm text-white/70 font-medium">Nenhuma movimentação registrada para este mês.</li>
            ) : (
              transacoesFiltradas.map(t => {
                const pago = t.status_pagamento === 'PAGO';
                return (
                  <li key={t.id} className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                      pago ? 'bg-white/20 text-white' : 'bg-black/10 text-white/60'
                    }`}>
                      <span className="material-symbols-outlined text-[18px]">
                        {pago ? 'check' : 'pending'}
                      </span>
                    </div>
                    <div className="flex-1">
                      <p className="font-body-sm text-body-sm font-semibold text-white">
                        R$ {t.valor.toFixed(2).replace('.', ',')}
                      </p>
                      <p className="font-label-bold text-label-bold text-white/80 font-normal capitalize">{t.tipo.toLowerCase()}</p>
                    </div>
                  </li>
                );
              })
            )}
          </ul>
        </div>
      </section>
    </div>
  );
}
