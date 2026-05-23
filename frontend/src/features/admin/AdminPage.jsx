import React, { useState } from 'react';
import { useEvento } from '../../hooks/useEvento';
import api from '../../services/api';
import { showToast } from '../../components/ui/Toast';

export function AdminPage() {
  const { 
    evento, 
    loading: loadingEvento, 
    error: errorEvento, 
    refetch, 
    criarEvento, 
    iniciarVotacao, 
    encerrarVotacao, 
    atualizarChurrasco, 
    cancelarEvento, 
    sortearTimes, 
    actionLoading 
  } = useEvento(1);
  
  const [loadingCheckin, setLoadingCheckin] = useState(null);
  const [timesSorteados, setTimesSorteados] = useState(null);

  // Form states for creating event
  const [dateStr, setDateStr] = useState('');
  const [timeStr, setTimeStr] = useState('10:00');
  const [hasBBQ, setHasBBQ] = useState(false);
  const [cota, setCota] = useState('50.00');

  const handleCheckin = async (usuarioId, chegou, falta_justificada = false) => {
    setLoadingCheckin(usuarioId);
    try {
      await api.post(`/eventos/1/checkin/${usuarioId}`, { chegou, falta_justificada });
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
      valor_churrasco: hasBBQ ? parseFloat(cota.replace(',', '.')) : 0.0
    });
  };

  const handleToggleChurrascoExistente = async () => {
    const newVal = !evento.flag_churrasco;
    const valor = newVal ? parseFloat(window.prompt("Qual o valor do churrasco? (ex: 50.00)", "50.00") || 0) : 0;
    await atualizarChurrasco(newVal, valor);
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

  const nenhumEventoAtivo = !evento || evento.status_evento === 'ENCERRADO' || evento.status_evento === 'CANCELADO';
  const presencaAberta = evento && evento.status_evento === 'PRESENCA_ABERTA';
  const votacaoAberta = evento && evento.status_evento === 'VOTACAO_ABERTA';
  const jogadoresConfirmados = evento?.presencas?.filter(p => p.status_jogo === 'VOU') || [];
  
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
        </section>
      )}

      {!nenhumEventoAtivo && (
        <div className="glass-panel rounded-xl p-4 ambient-shadow flex justify-between items-center mb-4">
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
      )}

      {presencaAberta && (
        <>
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
            
            <div className="grid grid-cols-2 gap-2 mt-2 pt-4 border-t border-surface-variant">
              <button onClick={() => handleSorteio('NOTA_ADMIN')} disabled={actionLoading} className="py-2 border border-outline text-on-surface rounded-lg font-label-bold text-label-bold hover:bg-surface-container-high">
                Sorteio (Admin)
              </button>
              <button onClick={() => handleSorteio('NOTA_GALERA')} disabled={actionLoading} className="py-2 border border-outline text-on-surface rounded-lg font-label-bold text-label-bold hover:bg-surface-container-high">
                Sorteio (Galera)
              </button>
            </div>
          </section>

          {timesSorteados && (
            <div className="space-y-4">
              <h3 className="font-headline-md text-headline-md text-on-surface flex gap-2 items-center">
                <span className="material-symbols-outlined">group</span> Times Sorteados
              </h3>
              <div className="grid grid-cols-2 gap-2">
                <div className="glass-panel rounded-xl p-3 shadow-ambient-1">
                  <h4 className="font-bold text-center border-b border-outline-variant/30 pb-2 mb-2">Time A ({timesSorteados.media_a?.toFixed(1)})</h4>
                  {timesSorteados.time_a.map(j => (
                    <div key={j.id} className="text-sm py-1 flex justify-between">
                      <span className="font-medium text-on-surface truncate pr-1">{j.nome.split(' ')[0]}</span>
                      <span className="text-[10px] text-tertiary bg-surface-variant px-1 rounded">{j.posicao}</span>
                    </div>
                  ))}
                </div>
                <div className="glass-panel rounded-xl p-3 shadow-ambient-1">
                  <h4 className="font-bold text-center border-b border-outline-variant/30 pb-2 mb-2">Time B ({timesSorteados.media_b?.toFixed(1)})</h4>
                  {timesSorteados.time_b.map(j => (
                    <div key={j.id} className="text-sm py-1 flex justify-between">
                      <span className="font-medium text-on-surface truncate pr-1">{j.nome.split(' ')[0]}</span>
                      <span className="text-[10px] text-tertiary bg-surface-variant px-1 rounded">{j.posicao}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          <section className="space-y-4">
            <h3 className="font-headline-md text-headline-md text-on-surface flex gap-2 items-center">
              <span className="material-symbols-outlined">how_to_reg</span> Check-in na Quadra
            </h3>
            {jogadoresConfirmados.length === 0 ? (
              <div className="text-center py-8 text-body-sm text-tertiary bg-surface-container-lowest rounded-xl shadow-ambient-1 border border-outline-variant/30">
                Nenhum jogador confirmou presença ainda.
              </div>
            ) : (
              <div className="space-y-3">
                {jogadoresConfirmados.map(jogador => {
                  const chegou = jogador.checkin_validado;
                  return (
                    <div key={jogador.usuario_id} className="glass-panel rounded-xl p-4 flex flex-col gap-3 shadow-ambient-1">
                      <div className="flex justify-between items-center border-b border-outline-variant/20 pb-2">
                        <span className="font-bold text-on-background text-[16px]">{jogador.usuario_nome}</span>
                        <div className="flex gap-2">
                          {jogador.vai_churrasco && <span className="text-[10px] font-bold px-2 py-0.5 bg-secondary-container/20 text-secondary-container rounded-full flex items-center gap-1"><span className="material-symbols-outlined text-[12px]">local_fire_department</span></span>}
                          <span className="text-[10px] font-bold px-2 py-0.5 bg-surface-variant text-tertiary rounded-full">{jogador.posicao}</span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button 
                          onClick={() => handleCheckin(jogador.usuario_id, true, false)}
                          disabled={loadingCheckin === jogador.usuario_id}
                          className={`py-2 text-[12px] font-bold uppercase flex-1 rounded-lg transition-colors ${chegou === true ? 'bg-primary text-on-primary' : 'bg-surface-variant text-on-surface-variant hover:bg-surface-container-high'}`}
                        >
                          Chegou
                        </button>
                        <button 
                          onClick={() => handleCheckin(jogador.usuario_id, false, false)}
                          disabled={loadingCheckin === jogador.usuario_id}
                          className={`py-2 text-[12px] font-bold uppercase flex-1 rounded-lg transition-colors ${chegou === false ? 'bg-error text-white' : 'border border-error text-error hover:bg-error/10'}`}
                        >
                          Faltou
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
          
          {evento.flag_churrasco && (
             <section className="space-y-4 pt-4">
               <h3 className="font-headline-md text-headline-md text-on-surface flex items-center gap-2"><span className="material-symbols-outlined text-secondary-container">local_fire_department</span> Lista do Churrasco</h3>
               <div className="glass-panel p-4 rounded-xl shadow-ambient-1">
                 <p className="font-label-bold text-label-bold text-tertiary mb-3">{confirmadosChurrasco.length} CONFIRMADOS</p>
                 <div className="flex flex-wrap gap-2">
                   {confirmadosChurrasco.map(p => (
                     <span key={p.usuario_id} className="text-body-sm font-medium bg-secondary-container/10 border border-secondary-container/20 text-secondary-container px-3 py-1 rounded-full">{p.usuario_nome.split(' ')[0]}</span>
                   ))}
                   {confirmadosChurrasco.length === 0 && <span className="text-body-sm text-tertiary">Ninguém confirmou ainda.</span>}
                 </div>
               </div>
             </section>
          )}
        </>
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
          <button 
            onClick={encerrarVotacao}
            disabled={actionLoading}
            className="w-full py-4 bg-error text-on-error rounded-xl font-headline-md text-headline-md shadow-lg hover:bg-error/90 active:scale-95 transition-all"
          >
            Encerrar Partida (Apurar Votos)
          </button>
        </section>
      )}

      {!nenhumEventoAtivo && (
        <section className="mt-8 mb-8">
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
      )}
    </div>
  );
}
