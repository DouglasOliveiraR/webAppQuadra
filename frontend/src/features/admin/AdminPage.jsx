import React, { useState, useEffect } from 'react';
import { useEvento } from '../../hooks/useEvento';
import api, { API_URL, getFotoUrl } from '../../services/api';
import { showToast } from '../../components/ui/Toast';

import { ElencoTab } from './ElencoTab';
import { AdminFinanceiroTab } from './AdminFinanceiroTab';
import { AdminAuditoriaTab } from './AdminAuditoriaTab';
import { AdminArtilhariaTab } from './AdminArtilhariaTab';

export function AdminPage() {
  const { 
    evento, 
    loading: loadingEvento, 
    error: errorEvento, 
    refetch, 
    criarEvento, 
    iniciarVotacao, 
    cancelarVotacao,
    encerrarVotacao, 
    atualizarChurrasco, 
    atualizarChavePix, 
    atualizarMensalidade, 
    atualizarCustoQuadra,
    cancelarEvento, 
    sortearTimes, 
    actionLoading 
  } = useEvento(1);
  
  const [loadingCheckin, setLoadingCheckin] = useState(null);
  const [timesSorteados, setTimesSorteados] = useState(null);
  const [activeTab, setActiveTab] = useState('geral');
  const [usuarios, setUsuarios] = useState([]);
  useEffect(() => {
    if (activeTab === 'check-in' && usuarios.length === 0) {
      api.get('/usuarios').then(res => setUsuarios(res.data)).catch(console.error);
    }
  }, [activeTab]);
  const [isCreatingNew, setIsCreatingNew] = useState(false);

  // Form states for creating event
  const [dateStr, setDateStr] = useState('');
  const [timeStr, setTimeStr] = useState('10:00');
  const [hasBBQ, setHasBBQ] = useState(false);
  const [cota, setCota] = useState('50.00');
  const [endereco, setEndereco] = useState('');

  // States para o modal de churrasco existente
  const [showChurrascoModal, setShowChurrascoModal] = useState(false);
  const [modalValorChurrasco, setModalValorChurrasco] = useState('50.00');

  // States para a chave pix
  const [chavePixInput, setChavePixInput] = useState('');
  const [showPixModal, setShowPixModal] = useState(false);
  const [modalChavePix, setModalChavePix] = useState('');

  // States para a mensalidade da quadra
  const [mensalidadeInput, setMensalidadeInput] = useState('60.00');
  const [showMensalidadeModal, setShowMensalidadeModal] = useState(false);
  const [modalValorMensalidade, setModalValorMensalidade] = useState('60.00');

  // States para o custo mensal da quadra
  const [custoQuadraInput, setCustoQuadraInput] = useState('600.00');
  const [showCustoQuadraModal, setShowCustoQuadraModal] = useState(false);
  const [modalValorCustoQuadra, setModalValorCustoQuadra] = useState('600.00');

  const handleCheckin = async (usuarioId, chegou, falta_justificada = false) => {
    setLoadingCheckin(usuarioId);
    try {
      await api.post(`/eventos/${evento.id}/checkin/${usuarioId}`, { chegou, falta_justificada });
      await refetch();
      showToast('Check-in atualizado com sucesso!');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao salvar checkin.';
      showToast(msg, 'error');
    } finally {
      setLoadingCheckin(null);
    }
  };

  const handleCriarEvento = async () => {
    let finalDate = dateStr;
    if (!finalDate) {
      const nextSaturday = new Date();
      nextSaturday.setDate(nextSaturday.getDate() + (6 - nextSaturday.getDay() + 7) % 7);
      finalDate = nextSaturday.toISOString().split('T')[0];
    }
    
    await criarEvento({
      data_jogo: finalDate,
      hora_inicio: timeStr + ':00',
      hora_fim: "12:00:00",
      flag_churrasco: hasBBQ,
      valor_churrasco: hasBBQ ? parseFloat(cota.replace(',', '.')) : 0.0,
      endereco: endereco,
      chave_pix: chavePixInput,
      valor_mensalidade: parseFloat(mensalidadeInput.replace(',', '.')) || 60.0,
      custo_quadra: parseFloat(custoQuadraInput.replace(',', '.')) || 0.0
    });
    setIsCreatingNew(false);
  };

  const handleConfirmarChurrascoModal = async () => {
    const valor = parseFloat(modalValorChurrasco.replace(',', '.')) || 0;
    setShowChurrascoModal(false);
    await atualizarChurrasco(true, valor);
  };

  const handleConfirmarPixModal = async () => {
    setShowPixModal(false);
    await atualizarChavePix(modalChavePix);
  };

  const handleEditarChavePix = () => {
    setModalChavePix(evento?.chave_pix || '');
    setShowPixModal(true);
  };

  const handleConfirmarMensalidadeModal = async () => {
    const valor = parseFloat(modalValorMensalidade.replace(',', '.')) || 60.0;
    setShowMensalidadeModal(false);
    await atualizarMensalidade(valor);
  };

  const handleEditarMensalidade = () => {
    setModalValorMensalidade(evento?.valor_mensalidade?.toFixed(2) || '60.00');
    setShowMensalidadeModal(true);
  };

  const handleConfirmarCustoQuadraModal = async () => {
    const valor = parseFloat(modalValorCustoQuadra.replace(',', '.')) || 0.0;
    setShowCustoQuadraModal(false);
    await atualizarCustoQuadra(valor);
  };

  const handleEditarCustoQuadra = () => {
    setModalValorCustoQuadra(evento?.custo_quadra?.toFixed(2) || '600.00');
    setShowCustoQuadraModal(true);
  };

  const handleToggleChurrascoExistente = async () => {
    if (evento.flag_churrasco) {
      await atualizarChurrasco(false, 0);
    } else {
      setModalValorChurrasco('50.00');
      setShowChurrascoModal(true);
    }
  };

  const handleSorteio = async (criterio) => {
    const times = await sortearTimes(criterio);
    if (times) {
      setTimesSorteados(times);
    }
  };

  const confirmCancelar = async () => {
    if (window.confirm("Tem certeza que deseja deletar/cancelar esta partida?")) {
      await cancelarEvento();
    }
  };

  if (loadingEvento) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary border-t-transparent"></div>
      </div>
    );
  }

  const nenhumEventoAtivo = !evento || evento.status_evento === 'CANCELADO' || isCreatingNew;
  const presencaAberta = evento && evento.status_evento === 'PRESENCA_ABERTA';
  const votacaoAberta = evento && evento.status_evento === 'VOTACAO_ABERTA';
  const jogadoresConfirmados = evento?.presencas?.filter(p => p.status_jogo === 'VOU') || [];
  let jogadoresCheckin = [];
  
  if (usuarios.length > 0) {
    const ativos = usuarios.filter(u => u.status === 'ATIVO');
    // We want ALL active MENSALISTA and ADMIN
    const fixos = ativos.filter(u => u.perfil === 'MENSALISTA' || u.perfil === 'ADMIN');
    // We also want ANY AVULSO who has a presenca record indicating they are going
    const presencasAvulsos = evento?.presencas?.filter(p => p.usuario_perfil === 'AVULSO' && p.status_jogo === 'VOU') || [];
    
    // We map fixos to have the 'checkin_validado', 'vai_churrasco' and 'posicao' from their presenca (if exists)
    // PERFORMANCE: Use O(1) Map lookup instead of O(N) Array.find to improve render performance for large groups
    const presencasMap = evento?.presencas?.reduce((acc, pres) => {
      acc[pres.usuario_id] = pres;
      return acc;
    }, {}) || {};

    const fixosMapped = fixos.map(u => {
      const p = presencasMap[u.id];
      return {
        usuario_id: u.id,
        usuario_nome: u.nome,
        usuario_perfil: u.perfil,
        usuario_foto_url: u.foto_url,
        posicao: p?.posicao || 'Linha', // Fallback if no presenca
        vai_churrasco: p?.vai_churrasco || false,
        checkin_validado: p?.checkin_validado || false,
        falta_penalizada: p?.falta_penalizada || false
      };
    });
    
    const avulsosMapped = presencasAvulsos.map(p => ({
      usuario_id: p.usuario_id,
      usuario_nome: p.usuario_nome,
      usuario_perfil: p.usuario_perfil,
      usuario_foto_url: p.usuario_foto_url,
      posicao: p.posicao,
      vai_churrasco: p.vai_churrasco,
      checkin_validado: p.checkin_validado,
      falta_penalizada: p.falta_penalizada
    }));
    
    // Sort alphabetically by name
    jogadoresCheckin = [...fixosMapped, ...avulsosMapped].sort((a, b) => a.usuario_nome.localeCompare(b.usuario_nome));
  } else {
    // Fallback to old behavior while loading
    jogadoresCheckin = evento?.presencas?.filter(
      p => p.status_jogo === 'VOU' || p.usuario_perfil === 'MENSALISTA' || p.usuario_perfil === 'ADMIN'
    ) || [];
  }
  
  const confirmadosChurrasco = evento?.presencas?.filter(p => p.vai_churrasco) || [];

  return (
    <div className="flex flex-col space-y-6 w-full">
      <header className="flex items-center justify-between mb-2">
        <h2 className="font-headline-md text-headline-md text-primary truncate flex-1 text-center">
          {nenhumEventoAtivo ? 'Configurar Rodada' : 'Painel de Controle'}
        </h2>
      </header>

      {errorEvento && (
        <div className="p-3 bg-error-container text-on-error-container text-body-sm rounded-standard border border-error/20">
          {errorEvento}
        </div>
      )}

      {nenhumEventoAtivo && (
        <section className="space-y-4">
          <h2 className="font-headline-md text-headline-md text-on-surface">Parâmetros do Jogo</h2>
          <div className="glass-panel rounded-xl p-4 ambient-shadow space-y-card-gap">
            <div className="space-y-1">
              <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider">Data do Jogo</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant">
                  <span className="material-symbols-outlined text-[20px]">calendar_today</span>
                </div>
                <input 
                  type="date" 
                  value={dateStr}
                  onChange={(e) => setDateStr(e.target.value)}
                  className="block w-full pl-10 pr-3 py-3 bg-[#F1F5F9] border-transparent rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-body-md text-on-surface"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider">Horário</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant">
                  <span className="material-symbols-outlined text-[20px]">schedule</span>
                </div>
                <input 
                  type="time" 
                  value={timeStr}
                  onChange={(e) => setTimeStr(e.target.value)}
                  className="block w-full pl-10 pr-3 py-3 bg-[#F1F5F9] border-transparent rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-body-md text-on-surface"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider">Endereço do Local</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant">
                  <span className="material-symbols-outlined text-[20px]">location_on</span>
                </div>
                <input 
                  type="text" 
                  value={endereco}
                  onChange={(e) => setEndereco(e.target.value)}
                  placeholder="Ex: Arena Oficial, Rua X, 123"
                  className="block w-full pl-10 pr-3 py-3 bg-[#F1F5F9] border-transparent rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-body-md text-on-surface"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider">Chave Pix do Recebedor</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant">
                  <span className="material-symbols-outlined text-[20px]">qr_code_2</span>
                </div>
                <input 
                  type="text" 
                  value={chavePixInput}
                  onChange={(e) => setChavePixInput(e.target.value)}
                  placeholder="Ex: Celular, E-mail ou Chave Aleatória"
                  className="block w-full pl-10 pr-3 py-3 bg-[#F1F5F9] border-transparent rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-body-md text-on-surface"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider">Mensalidade da Quadra (R$)</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant">
                  <span className="material-symbols-outlined text-[20px]">payments</span>
                </div>
                <input 
                  type="text" 
                  value={mensalidadeInput}
                  onChange={(e) => setMensalidadeInput(e.target.value)}
                  placeholder="60.00"
                  className="block w-full pl-10 pr-3 py-3 bg-[#F1F5F9] border-transparent rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-body-md text-on-surface"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider">Custo Mensal da Quadra (R$)</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant">
                  <span className="material-symbols-outlined text-[20px]">account_balance</span>
                </div>
                <input 
                  type="text" 
                  value={custoQuadraInput}
                  onChange={(e) => setCustoQuadraInput(e.target.value)}
                  placeholder="600.00"
                  className="block w-full pl-10 pr-3 py-3 bg-[#F1F5F9] border-transparent rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-body-md text-on-surface"
                />
              </div>
            </div>
            
            <hr className="border-surface-variant my-2" />
            
            <div className="flex items-center justify-between py-2">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-secondary-container/20 flex items-center justify-center text-secondary-container">
                  <span className="material-symbols-outlined">restaurant</span>
                </div>
                <div>
                  <span className="block font-headline-md text-headline-md text-on-surface text-[16px]">Vai ter Churrasco?</span>
                  <span className="block font-body-sm text-body-sm text-on-surface-variant text-[12px]">Habilita a coleta de cota.</span>
                </div>
              </div>
              <div className="relative inline-block w-12 mr-2 align-middle select-none transition duration-200 ease-in">
                <input 
                  type="checkbox" 
                  id="bbq-toggle" 
                  checked={hasBBQ}
                  onChange={(e) => setHasBBQ(e.target.checked)}
                  className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer z-10 transition-transform duration-200 ease-in-out border-surface-variant"
                />
                <label htmlFor="bbq-toggle" className="toggle-label block overflow-hidden h-6 rounded-full bg-surface-variant cursor-pointer transition-colors duration-200 ease-in-out"></label>
              </div>
            </div>

            {hasBBQ && (
              <div className="space-y-1 fade-in">
                <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider">Valor da Cota</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant font-headline-md font-bold">R$</div>
                  <input 
                    type="text"
                    value={cota}
                    onChange={(e) => setCota(e.target.value)}
                    className="block w-full pl-10 pr-3 py-3 bg-[#F1F5F9] border-transparent rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-body-md text-on-surface font-bold"
                  />
                </div>
              </div>
            )}
          </div>
          
          <button 
            onClick={handleCriarEvento}
            disabled={actionLoading}
            className="w-full mt-6 py-4 bg-primary text-on-primary rounded-xl font-headline-md text-headline-md text-[16px] shadow-lg shadow-primary/20 hover:bg-primary/90 active:scale-95 transition-all flex items-center justify-center gap-2"
          >
            <span className="material-symbols-outlined">save</span>
            Salvar Configurações
          </button>
          
          {evento && evento.status_evento !== 'CANCELADO' && (
            <button 
              onClick={() => setIsCreatingNew(false)}
              className="w-full mt-2 py-3 border-2 border-outline-variant text-on-surface rounded-xl font-label-bold text-label-bold hover:bg-surface-variant/50 transition-colors"
            >
              Cancelar e Voltar ao Evento
            </button>
          )}
        </section>
      )}

      {!nenhumEventoAtivo && (
        <div className="flex border-b border-outline-variant/30 mb-4 overflow-x-auto hide-scrollbar">
          {['geral', 'check-in', 'elenco', 'sorteio', 'financeiro', 'auditoria', 'artilharia'].map(tab => (
            <button 
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-3 text-[14px] font-label-bold capitalize whitespace-nowrap transition-colors ${
                activeTab === tab 
                  ? 'text-primary border-b-2 border-primary' 
                  : 'text-on-surface-variant hover:bg-surface-container-low'
              }`}
            >
              {tab.replace('-', ' ')}
            </button>
          ))}
        </div>
      )}

      {!nenhumEventoAtivo && activeTab === 'geral' && (
        <div className="space-y-4 fade-in">
          {evento.status_evento === 'ENCERRADO' && (
            <div className="bg-primary/10 border border-primary/20 rounded-xl p-5 mb-6 text-center space-y-4">
              <div className="w-16 h-16 bg-primary text-on-primary rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="material-symbols-outlined text-[32px]">check_circle</span>
              </div>
              <h3 className="font-headline-md text-headline-md text-primary">Partida Encerrada</h3>
              <p className="font-body-sm text-body-sm text-on-surface-variant">Os votos já foram apurados e os dados foram salvos. Você ainda pode editar o financeiro ou ver o elenco desta partida.</p>
              <button 
                onClick={() => setIsCreatingNew(true)}
                className="w-full py-3 bg-primary text-on-primary rounded-xl font-label-bold text-label-bold hover:bg-primary/90 active:scale-95 transition-all flex items-center justify-center gap-2 mt-4 shadow-lg shadow-primary/20"
              >
                <span className="material-symbols-outlined">add_circle</span>
                Começar Nova Rodada
              </button>
            </div>
          )}

          <div className="glass-panel rounded-xl p-4 ambient-shadow flex justify-between items-center">
            <div className="flex items-center gap-3">
              <span className={`material-symbols-outlined text-[24px] ${evento.flag_churrasco ? 'text-secondary-container' : 'text-tertiary'}`}>local_fire_department</span>
              <div>
                <h3 className="font-bold">Churrasco: {evento.flag_churrasco ? 'Ativo' : 'Inativo'}</h3>
                {evento.flag_churrasco && <p className="text-sm text-tertiary">R$ {evento.valor_churrasco?.toFixed(2)} / pessoa</p>}
              </div>
            </div>
            <button 
              onClick={handleToggleChurrascoExistente} 
              disabled={actionLoading}
              className="px-3 py-1.5 border-2 border-outline-variant text-on-surface rounded-lg font-label-bold text-label-bold hover:bg-surface-variant/50"
            >
              {evento.flag_churrasco ? 'Desativar' : 'Ativar'}
            </button>
          </div>

          <div className="glass-panel rounded-xl p-4 ambient-shadow flex justify-between items-center">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-[24px] text-primary">qr_code_2</span>
              <div>
                <h3 className="font-bold">Chave Pix de Recebimento</h3>
                <p className="text-sm text-tertiary">{evento.chave_pix || 'Nenhuma chave cadastrada'}</p>
              </div>
            </div>
            <button 
              onClick={handleEditarChavePix} 
              disabled={actionLoading}
              className="px-3 py-1.5 border-2 border-outline-variant text-on-surface rounded-lg font-label-bold text-label-bold hover:bg-surface-variant/50"
            >
              Configurar
            </button>
          </div>

          <div className="glass-panel rounded-xl p-4 ambient-shadow flex justify-between items-center">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-[24px] text-primary">payments</span>
              <div>
                <h3 className="font-bold">Mensalidade da Quadra</h3>
                <p className="text-sm text-tertiary">R$ {evento.valor_mensalidade?.toFixed(2).replace('.', ',') || '60,00'}</p>
              </div>
            </div>
            <button 
              onClick={handleEditarMensalidade} 
              disabled={actionLoading}
              className="px-3 py-1.5 border-2 border-outline-variant text-on-surface rounded-lg font-label-bold text-label-bold hover:bg-surface-variant/50"
            >
              Configurar
            </button>
          </div>

          <div className="glass-panel rounded-xl p-4 ambient-shadow flex justify-between items-center">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-[24px] text-primary">account_balance</span>
              <div>
                <h3 className="font-bold">Mensal da Quadra (Custo)</h3>
                <p className="text-sm text-tertiary">R$ {evento.custo_quadra?.toFixed(2).replace('.', ',') || '0,00'}</p>
              </div>
            </div>
            <button 
              onClick={handleEditarCustoQuadra} 
              disabled={actionLoading}
              className="px-3 py-1.5 border-2 border-outline-variant text-on-surface rounded-lg font-label-bold text-label-bold hover:bg-surface-variant/50"
            >
              Configurar
            </button>
          </div>

          {presencaAberta && (
            <section className="glass-panel rounded-xl p-4 ambient-shadow border-l-4 border-secondary-container flex flex-col gap-4">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-bold text-lg">Ações da Quadra</h3>
                </div>
                <button 
                  onClick={iniciarVotacao}
                  disabled={actionLoading}
                  className="bg-primary text-on-primary px-3 py-2 rounded-lg font-label-bold flex gap-2 items-center text-label-bold hover:bg-primary/90"
                >
                  <span className="material-symbols-outlined text-[16px]">how_to_vote</span> Votação
                </button>
              </div>
            </section>
          )}

          {votacaoAberta && (
            <section className="glass-panel rounded-xl p-6 shadow-ambient-1 border-l-4 border-error flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-[32px] text-error">stop_circle</span>
                <div>
                  <h3 className="font-headline-md text-headline-md text-on-surface">Fase de Votação</h3>
                  <p className="font-body-sm text-body-sm text-tertiary">Jogadores estão votando nos prêmios da partida.</p>
                </div>
              </div>
              <div className="flex flex-col gap-2">
                <button 
                  onClick={encerrarVotacao}
                  disabled={actionLoading}
                  className="w-full py-4 bg-error text-on-error rounded-xl font-headline-md text-headline-md shadow-lg hover:bg-error/90 active:scale-95 transition-all"
                >
                  Encerrar Partida (Apurar Votos)
                </button>
                <button 
                  onClick={cancelarVotacao}
                  disabled={actionLoading}
                  className="w-full py-2 bg-transparent text-tertiary border-2 border-tertiary/20 rounded-xl font-label-lg hover:bg-tertiary/10 active:scale-95 transition-all"
                >
                  Desfazer (Voltar para Presenças)
                </button>
              </div>
            </section>
          )}

          <section className="mt-8 mb-4">
            <div className="bg-error-container/50 border border-error/20 rounded-xl p-5 space-y-4">
              <h3 className="font-headline-md text-headline-md text-error flex items-center gap-2">
                <span className="material-symbols-outlined">warning</span>
                Zona de Perigo
              </h3>
              <p className="font-body-sm text-body-sm text-on-surface-variant">Ações destrutivas não podem ser desfeitas. Notificará todos os jogadores confirmados.</p>
              <button 
                onClick={confirmCancelar} 
                disabled={actionLoading}
                className="w-full py-3 border-2 border-error text-error rounded-xl font-label-bold text-label-bold uppercase tracking-wider hover:bg-error/10 active:bg-error/20 transition-colors flex items-center justify-center gap-2"
              >
                <span className="material-symbols-outlined">cancel</span>
                Cancelar Pelada
              </button>
            </div>
          </section>
        </div>
      )}

      {!nenhumEventoAtivo && activeTab === 'check-in' && (
        <div className="space-y-4 fade-in">
          {/* Check-in Progress Bar Placeholder */}
          <div className="glass-panel rounded-xl p-4 shadow-ambient-1 bg-primary/10 border border-primary/20">
            <div className="flex justify-between text-body-sm font-bold text-primary mb-2 uppercase">
              <span>Jogadores Presentes</span>
              <span>{jogadoresCheckin.filter(j => j.checkin_validado).length} de {jogadoresCheckin.length}</span>
            </div>
            <div className="w-full bg-surface-variant rounded-full h-2.5">
              <div 
                className="bg-primary h-2.5 rounded-full transition-all duration-500" 
                style={{ width: `${jogadoresCheckin.length ? (jogadoresCheckin.filter(j => j.checkin_validado).length / jogadoresCheckin.length) * 100 : 0}%` }}
              ></div>
            </div>
          </div>

          <section className="space-y-4">
            <h3 className="font-headline-md text-headline-md text-on-surface flex gap-2 items-center">
              <span className="material-symbols-outlined">how_to_reg</span> Check-in na Quadra
            </h3>
            {jogadoresCheckin.length === 0 ? (
              <div className="text-center py-8 text-body-sm text-tertiary bg-surface-container-lowest rounded-xl shadow-ambient-1 border border-outline-variant/30">
                Nenhum jogador para check-in.
              </div>
            ) : (
              <div className="space-y-3">
                {jogadoresCheckin.map(jogador => {
                  const presente = jogador.checkin_validado;
                  const faltou = jogador.falta_penalizada;
                  const pendente = !presente && !faltou;
                  return (
                    <div key={jogador.usuario_id} className="glass-panel rounded-xl p-4 flex flex-col gap-3 shadow-ambient-1">
                      <div className="flex justify-between items-center border-b border-outline-variant/20 pb-2">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-surface-variant flex items-center justify-center text-on-surface-variant text-xs font-bold shrink-0 overflow-hidden">
                            {jogador.usuario_foto_url ? (
                              <img src={getFotoUrl(jogador.usuario_foto_url)} alt={jogador.usuario_nome} className="w-full h-full object-cover" />
                            ) : (
                              jogador.usuario_nome.charAt(0)
                            )}
                          </div>
                          <span className="font-bold text-on-background text-[16px]">{jogador.usuario_nome}</span>
                        </div>
                        <div className="flex gap-2">
                          {jogador.vai_churrasco && <span className="text-[10px] font-bold px-2 py-0.5 bg-secondary-container/20 text-secondary-container rounded-full flex items-center gap-1"><span className="material-symbols-outlined text-[12px]">local_fire_department</span></span>}
                          <span className="text-[10px] font-bold px-2 py-0.5 bg-surface-variant text-tertiary rounded-full">{jogador.posicao}</span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button 
                          onClick={() => handleCheckin(jogador.usuario_id, false, true)}
                          disabled={loadingCheckin === jogador.usuario_id}
                          className={`py-2 text-[12px] font-bold uppercase flex-1 rounded-lg transition-colors ${pendente ? 'bg-surface-variant text-on-surface' : 'border border-surface-variant text-on-surface-variant hover:bg-surface-container-high'}`}
                        >
                          <span className="material-symbols-outlined text-[16px] align-text-bottom mr-1">schedule</span>
                          Pendente
                        </button>
                        <button 
                          onClick={() => handleCheckin(jogador.usuario_id, true, false)}
                          disabled={loadingCheckin === jogador.usuario_id}
                          className={`py-2 text-[12px] font-bold uppercase flex-1 rounded-lg transition-colors ${presente ? 'bg-primary text-on-primary' : 'border border-primary/50 text-primary hover:bg-primary/10'}`}
                        >
                          <span className="material-symbols-outlined text-[16px] align-text-bottom mr-1">check_circle</span>
                          Chegou
                        </button>
                        <button 
                          onClick={() => handleCheckin(jogador.usuario_id, false, false)}
                          disabled={loadingCheckin === jogador.usuario_id}
                          className={`py-2 text-[12px] font-bold uppercase flex-1 rounded-lg transition-colors ${faltou ? 'bg-error text-white' : 'border border-error/50 text-error hover:bg-error/10'}`}
                        >
                          <span className="material-symbols-outlined text-[16px] align-text-bottom mr-1">cancel</span>
                          Faltou
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        </div>
      )}

      {!nenhumEventoAtivo && activeTab === 'elenco' && (
        <ElencoTab />
      )}

      {!nenhumEventoAtivo && activeTab === 'sorteio' && (
        <div className="space-y-4 fade-in">
          {presencaAberta && (
            <section className="glass-panel rounded-xl p-4 ambient-shadow border border-outline-variant/30 flex flex-col gap-4">
              <h3 className="font-bold text-lg border-b border-surface-variant pb-2">Base do Sorteio</h3>
              <div className="grid grid-cols-1 gap-3 mt-2">
                <button onClick={() => handleSorteio('NOTA_ADMIN')} disabled={actionLoading} className="py-3 px-4 border border-outline text-on-surface rounded-lg font-label-bold text-label-bold hover:bg-primary/10 hover:border-primary text-left flex justify-between items-center transition-colors">
                  <span>Usar Minha Nota (Admin)</span>
                  <span className="material-symbols-outlined text-tertiary">chevron_right</span>
                </button>
                <button onClick={() => handleSorteio('NOTA_GALERA')} disabled={actionLoading} className="py-3 px-4 border border-outline text-on-surface rounded-lg font-label-bold text-label-bold hover:bg-primary/10 hover:border-primary text-left flex justify-between items-center transition-colors">
                  <span>Usar Nota da Galera (Média)</span>
                  <span className="material-symbols-outlined text-tertiary">chevron_right</span>
                </button>
              </div>
            </section>
          )}

          {timesSorteados && (
            <div className="space-y-4 mt-6">
              <div className="flex justify-between items-center">
                <h3 className="font-headline-md text-headline-md text-on-surface flex gap-2 items-center">
                  <span className="material-symbols-outlined">group</span> Times Gerados
                </h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {timesSorteados.times?.map((time, idx) => (
                  <div key={idx} className="glass-panel rounded-xl p-0 shadow-ambient-1 overflow-hidden flex flex-col">
                    <div className="bg-surface-container-high px-4 py-3 flex justify-between items-center">
                      <h4 className="font-bold text-[16px]">{time.nome}</h4>
                      <span className="text-sm font-medium bg-surface-lowest px-2 py-1 rounded border border-outline-variant/30">Força Média: {time.media?.toFixed(1)}</span>
                    </div>
                    <div className="divide-y divide-outline-variant/30 flex-1 bg-surface-container-lowest">
                      {time.jogadores.map(j => (
                        <div key={j.id} className="px-4 py-3 flex justify-between items-center hover:bg-surface-variant/30 transition-colors">
                          <span className="font-medium text-on-surface flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${j.posicao === 'GOL' ? 'bg-secondary' : 'bg-primary'}`}></div>
                            {j.nome}
                          </span>
                          <span className={`text-[10px] font-bold px-2 py-1 rounded ${j.posicao === 'GOL' ? 'bg-secondary-container/20 text-secondary-container' : 'bg-surface-variant text-tertiary'}`}>{j.posicao}</span>
                        </div>
                      ))}
                    </div>
                    <div className="bg-surface-container-low px-4 py-2 text-xs text-tertiary text-right border-t border-outline-variant/30">
                      {time.jogadores.length} jogadores
                    </div>
                  </div>
                ))}
              </div>

              {timesSorteados.sugestoes_banco && timesSorteados.sugestoes_banco.length > 0 && (
                <div className="mt-8 space-y-4 animate-fade-in">
                  <div className="flex items-center gap-2 border-b border-outline-variant/30 pb-2">
                    <span className="material-symbols-outlined text-secondary">transfer_within_a_station</span>
                    <h3 className="font-headline-sm text-headline-sm text-on-surface">Sugestões de Banco</h3>
                  </div>
                  
                  {timesSorteados.sugestoes_banco.map((sug, idx) => (
                    <div key={idx} className="glass-panel bg-surface-container-lowest rounded-xl p-4 border border-outline-variant/30 shadow-ambient-1 space-y-3">
                      <p className="font-medium text-sm text-on-surface-variant">
                        O <strong className="text-on-surface">{sug.time_incompleto}</strong> precisa de <strong className="text-secondary">{sug.vagas}</strong> jogador(es). Para manter o time com a média equilibrada do jogo, sugerimos puxar:
                      </p>
                      
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">
                        {sug.opcoes.map((opcao, opIdx) => (
                          <div key={opIdx} className="bg-surface rounded-lg p-3 border border-outline-variant/20 flex flex-col gap-2 relative overflow-hidden">
                            <div className="absolute top-0 left-0 w-1 h-full bg-primary/40"></div>
                            <div className="flex justify-between items-center text-xs pl-2">
                              <span className="font-bold text-tertiary">Opção do {opcao.origem}</span>
                              <span className="font-medium text-on-surface-variant bg-surface-variant px-2 py-0.5 rounded">Média Simulada: {opcao.media_simulada?.toFixed(1)}</span>
                            </div>
                            <div className="space-y-1 pl-2">
                              {opcao.jogadores.map(j => (
                                <div key={j.id} className="flex justify-between items-center bg-surface-container-low px-2 py-1.5 rounded">
                                  <span className="text-sm font-medium">{j.nome}</span>
                                  <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${j.posicao === 'GOL' ? 'bg-secondary-container/20 text-secondary-container' : 'bg-surface-variant text-tertiary'}`}>{j.posicao}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {!nenhumEventoAtivo && activeTab === 'financeiro' && (
        <AdminFinanceiroTab />
      )}

      {!nenhumEventoAtivo && activeTab === 'auditoria' && (
        <AdminAuditoriaTab eventoId={evento.id} />
      )}

      {!nenhumEventoAtivo && activeTab === 'artilharia' && (
        <AdminArtilhariaTab eventoId={evento.id} presencas={presencasTodas} />
      )}

      {/* Modal de Configuração do Churrasco */}
      {showChurrascoModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-surface dark:bg-surface-dim rounded-2xl w-full max-w-sm p-6 shadow-2xl border border-outline-variant/30 animate-scale-up space-y-4">
            <div className="flex items-center gap-3 border-b border-outline-variant/20 pb-3">
              <div className="w-10 h-10 rounded-full bg-secondary-container/20 text-secondary-container flex items-center justify-center">
                <span className="material-symbols-outlined">local_fire_department</span>
              </div>
              <div>
                <h3 className="font-headline-sm text-headline-sm text-on-surface">Configurar Churrasco</h3>
                <p className="font-body-sm text-body-sm text-tertiary">Defina a taxa de participação por pessoa</p>
              </div>
            </div>

            <div className="space-y-2">
              <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider">Cota do Churrasco (R$)</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant">
                  <span className="material-symbols-outlined text-[20px]">payments</span>
                </div>
                <input 
                  type="text" 
                  value={modalValorChurrasco}
                  onChange={(e) => setModalValorChurrasco(e.target.value)}
                  placeholder="0.00"
                  className="block w-full pl-10 pr-3 py-3 bg-[#F1F5F9] dark:bg-surface-lowest border-transparent rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-body-md text-on-surface"
                  autoFocus
                />
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <button 
                onClick={() => setShowChurrascoModal(false)}
                className="flex-1 py-3 border-2 border-outline-variant text-on-surface rounded-xl font-label-bold text-label-bold hover:bg-surface-variant/50 transition-colors"
              >
                Cancelar
              </button>
              <button 
                onClick={handleConfirmarChurrascoModal}
                disabled={actionLoading}
                className="flex-1 py-3 bg-primary text-on-primary rounded-xl font-label-bold text-label-bold hover:bg-primary/90 transition-colors disabled:opacity-50"
              >
                Confirmar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Configuração da Chave Pix */}
      {showPixModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-surface dark:bg-surface-dim rounded-2xl w-full max-w-sm p-6 shadow-2xl border border-outline-variant/30 animate-scale-up space-y-4">
            <div className="flex items-center gap-3 border-b border-outline-variant/20 pb-3">
              <div className="w-10 h-10 rounded-full bg-primary/20 text-primary flex items-center justify-center">
                <span className="material-symbols-outlined">qr_code_2</span>
              </div>
              <div>
                <h3 className="font-headline-sm text-headline-sm text-on-surface">Configurar Chave Pix</h3>
                <p className="font-body-sm text-body-sm text-tertiary">Chave Pix para recebimento das taxas</p>
              </div>
            </div>

            <div className="space-y-2">
              <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider">Chave Pix</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant">
                  <span className="material-symbols-outlined text-[20px]">vpn_key</span>
                </div>
                <input 
                  type="text" 
                  value={modalChavePix}
                  onChange={(e) => setModalChavePix(e.target.value)}
                  placeholder="CPF, E-mail, Celular ou Aleatória"
                  className="block w-full pl-10 pr-3 py-3 bg-[#F1F5F9] dark:bg-surface-lowest border-transparent rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-body-md text-on-surface"
                  autoFocus
                />
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <button 
                onClick={() => setShowPixModal(false)}
                className="flex-1 py-3 border-2 border-outline-variant text-on-surface rounded-xl font-label-bold text-label-bold hover:bg-surface-variant/50 transition-colors"
              >
                Cancelar
              </button>
              <button 
                onClick={handleConfirmarPixModal}
                disabled={actionLoading}
                className="flex-1 py-3 bg-primary text-on-primary rounded-xl font-label-bold text-label-bold hover:bg-primary/90 transition-colors disabled:opacity-50"
              >
                Confirmar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Configuração da Mensalidade */}
      {showMensalidadeModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-surface dark:bg-surface-dim rounded-2xl w-full max-w-sm p-6 shadow-2xl border border-outline-variant/30 animate-scale-up space-y-4">
            <div className="flex items-center gap-3 border-b border-outline-variant/20 pb-3">
              <div className="w-10 h-10 rounded-full bg-primary/20 text-primary flex items-center justify-center">
                <span className="material-symbols-outlined">payments</span>
              </div>
              <div>
                <h3 className="font-headline-sm text-headline-sm text-on-surface">Configurar Mensalidade</h3>
                <p className="font-body-sm text-body-sm text-tertiary">Valor da mensalidade padrão dos mensalistas</p>
              </div>
            </div>

            <div className="space-y-2">
              <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider">Cota da Mensalidade (R$)</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant font-headline-md font-bold">R$</div>
                <input 
                  type="text" 
                  value={modalValorMensalidade}
                  onChange={(e) => setModalValorMensalidade(e.target.value)}
                  placeholder="60.00"
                  className="block w-full pl-10 pr-3 py-3 bg-[#F1F5F9] dark:bg-surface-lowest border-transparent rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-body-md text-on-surface font-bold"
                  autoFocus
                />
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <button 
                onClick={() => setShowMensalidadeModal(false)}
                className="flex-1 py-3 border-2 border-outline-variant text-on-surface rounded-xl font-label-bold text-label-bold hover:bg-surface-variant/50 transition-colors"
              >
                Cancelar
              </button>
              <button 
                onClick={handleConfirmarMensalidadeModal}
                disabled={actionLoading}
                className="flex-1 py-3 bg-primary text-on-primary rounded-xl font-label-bold text-label-bold hover:bg-primary/90 transition-colors disabled:opacity-50"
              >
                Confirmar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Configuração do Custo Mensal da Quadra */}
      {showCustoQuadraModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-surface dark:bg-surface-dim rounded-2xl w-full max-w-sm p-6 shadow-2xl border border-outline-variant/30 animate-scale-up space-y-4">
            <div className="flex items-center gap-3 border-b border-outline-variant/20 pb-3">
              <div className="w-10 h-10 rounded-full bg-primary/20 text-primary flex items-center justify-center">
                <span className="material-symbols-outlined">account_balance</span>
              </div>
              <div>
                <h3 className="font-headline-sm text-headline-sm text-on-surface">Configurar Custo Mensal</h3>
                <p className="font-body-sm text-body-sm text-tertiary">Valor de custo do aluguel mensal da quadra</p>
              </div>
            </div>

            <div className="space-y-2">
              <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider">Custo da Quadra (R$)</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant font-headline-md font-bold">R$</div>
                <input 
                  type="text" 
                  value={modalValorCustoQuadra}
                  onChange={(e) => setModalValorCustoQuadra(e.target.value)}
                  placeholder="600.00"
                  className="block w-full pl-10 pr-3 py-3 bg-[#F1F5F9] dark:bg-surface-lowest border-transparent rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-body-md text-on-surface font-bold"
                  autoFocus
                />
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <button 
                onClick={() => setShowCustoQuadraModal(false)}
                className="flex-1 py-3 border-2 border-outline-variant text-on-surface rounded-xl font-label-bold text-label-bold hover:bg-surface-variant/50 transition-colors"
              >
                Cancelar
              </button>
              <button 
                onClick={handleConfirmarCustoQuadraModal}
                disabled={actionLoading}
                className="flex-1 py-3 bg-primary text-on-primary rounded-xl font-label-bold text-label-bold hover:bg-primary/90 transition-colors disabled:opacity-50"
              >
                Confirmar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>

  );
}
