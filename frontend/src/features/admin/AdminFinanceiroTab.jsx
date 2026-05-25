import React, { useState, useEffect } from 'react';
import api, { API_URL } from '../../services/api';
import { useFinanceiro } from '../../hooks/useFinanceiro';

export function AdminFinanceiroTab() {
  const [eventos, setEventos] = useState([]);
  const { 
    pendenciasAdmin, 
    loadingAdmin, 
    actionLoading, 
    errorAdmin, 
    baixarPagamentoAdmin, 
    refetchAdmin 
  } = useFinanceiro();

  const [subTab, setSubTab] = useState('mensalidades'); // 'mensalidades' | 'churrasco'
  
  const getMesAtual = () => {
    const hoje = new Date();
    const ano = hoje.getFullYear();
    const mes = String(hoje.getMonth() + 1).padStart(2, '0');
    return `${ano}-${mes}`;
  };

  const [selectedMonth, setSelectedMonth] = useState(getMesAtual());

  useEffect(() => {
    if (subTab === 'mensalidades') {
      refetchAdmin(selectedMonth);
    }
  }, [subTab, selectedMonth]);

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

  const jogadoresConfirmados = eventoDoMes?.presencas?.filter(p => p.vai_churrasco) || [];
  const cota = eventoDoMes?.valor_churrasco || 40;
  const meta = 600; // Mock goal para o churrasco
  const arrecadado = jogadoresConfirmados.length * cota;
  const faltam = Math.max(0, meta - arrecadado);
  const progresso = Math.min(100, (arrecadado / meta) * 100);

  // Filtrar apenas mensalidades
  const mensalidades = pendenciasAdmin.filter(item => item.tipo === 'MENSALIDADE') || [];

  const gerarMesesOpcoes = () => {
    const anoAtual = new Date().getFullYear();
    const meses = [
      "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
      "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ];
    return meses.map((nome, index) => {
      const mesNum = String(index + 1).padStart(2, '0');
      return {
        value: `${anoAtual}-${mesNum}`,
        label: `${nome} / ${anoAtual}`
      };
    });
  };

  const mesesOpcoes = gerarMesesOpcoes();

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
                      <div className="w-10 h-10 rounded-full bg-surface-variant flex items-center justify-center text-on-surface-variant font-bold text-sm shrink-0 overflow-hidden">
                        {jogador.usuario_foto_url ? (
                          <img src={`${API_URL}${jogador.usuario_foto_url}`} alt={jogador.usuario_nome} className="w-full h-full object-cover" />
                        ) : (
                          jogador.usuario_nome.charAt(0)
                        )}
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
        <div className="space-y-4">
          <h3 className="font-headline-md text-headline-md text-on-surface flex justify-between items-center flex-wrap gap-3">
            <span>Mensalidades dos Jogadores</span>
            <div className="flex items-center gap-2">
              <select 
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(e.target.value)}
                className="bg-surface-container-high border-2 border-outline-variant/30 text-on-surface text-sm rounded-lg px-3 py-2 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all font-body-md"
              >
                {mesesOpcoes.map(m => (
                  <option key={m.value} value={m.value} className="bg-surface text-on-surface">{m.label}</option>
                ))}
              </select>
              <button 
                onClick={() => refetchAdmin(selectedMonth)}
                className="p-2 text-primary hover:bg-primary/10 rounded-full transition-colors flex items-center justify-center shrink-0"
                title="Atualizar lista"
              >
                <span className="material-symbols-outlined text-[20px]">refresh</span>
              </button>
            </div>
          </h3>

          {errorAdmin && (
            <div className="p-3 bg-error-container text-on-error-container text-body-sm rounded-standard font-medium">
              {errorAdmin}
            </div>
          )}

          {loadingAdmin ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-4 border-primary border-t-transparent"></div>
            </div>
          ) : mensalidades.length === 0 ? (
            <div className="text-center py-10 bg-surface-container-low rounded-xl border border-outline-variant/30 shadow-inner">
              <span className="material-symbols-outlined text-[48px] text-tertiary mb-3">payments</span>
              <h4 className="font-headline-sm text-on-surface mb-1">Nenhuma Mensalidade Cadastrada</h4>
              <p className="text-body-sm text-on-surface-variant px-4">Cadastre jogadores com perfil Mensalistas ou Admin no elenco para gerenciar as mensalidades.</p>
            </div>
          ) : (
            <div className="glass-panel rounded-xl overflow-hidden shadow-ambient-1 divide-y divide-outline-variant/30">
              {mensalidades.map((item) => {
                const isPago = item.status_pagamento === 'PAGO';
                return (
                  <div key={item.id} className="p-4 flex items-center justify-between bg-surface-container-lowest hover:bg-surface-container-low/30 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm shrink-0">
                        <span className="material-symbols-outlined">person</span>
                      </div>
                      <div>
                        <span className="block font-bold text-[16px] text-on-surface">{item.usuario_nome || 'Jogador'}</span>
                        {item.usuario_telefone && (
                          <span className="block text-[12px] text-tertiary font-medium">{item.usuario_telefone}</span>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <span className="block font-extrabold text-[15px] text-on-surface">R$ {item.valor.toFixed(2).replace('.', ',')}</span>
                        <span className={`inline-block text-[10px] font-bold px-2 py-0.5 rounded-full mt-1 ${
                          isPago ? 'bg-primary/20 text-primary' : 'bg-warning/20 text-warning-active'
                        }`}>
                          {isPago ? 'Pago' : 'Pendente'}
                        </span>
                      </div>

                      <button 
                        onClick={() => !isPago && baixarPagamentoAdmin(item.id, selectedMonth)}
                        disabled={actionLoading || isPago}
                        className={`px-4 py-2 rounded-lg font-label-bold text-label-bold border transition-all ${
                          isPago 
                            ? 'bg-primary border-primary text-on-primary opacity-90 cursor-default' 
                            : 'bg-transparent border-primary text-primary hover:bg-primary/10 active:scale-95 disabled:opacity-50'
                        }`}
                      >
                        {isPago ? (
                          <span className="flex items-center gap-1">
                            <span className="material-symbols-outlined text-[16px]">check</span>
                            Baixado
                          </span>
                        ) : (
                          'Dar Baixa'
                        )}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
