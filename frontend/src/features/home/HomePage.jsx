import React, { useState, useEffect } from 'react';
import { useEvento } from '../../hooks/useEvento';
import api, { getFotoUrl } from '../../services/api';

export function HomePage() {
  const { evento, loading, actionLoading, error, atualizarPresenca } = useEvento(1);
  const [showPositionSelection, setShowPositionSelection] = useState(false);
  const [meusDados, setMeusDados] = useState(null);

  useEffect(() => {
    // Busca dados do próprio usuário (pontos, notas)
    const fetchMe = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) return;
        const payloadBase64 = token.split('.')[1];
        const decodedPayload = JSON.parse(atob(payloadBase64));
        const currentUserId = parseInt(decodedPayload.sub);
        // Podemos tentar buscar o ranking para pegar as estatísticas, ou usar mock
        // Para MVP, pegamos do ranking se existir
        const { data } = await api.get('/ranking');
        const eu = data.find(u => u.id === currentUserId);
        if (eu) setMeusDados(eu);
      } catch (err) {
        console.error('Erro ao buscar meus dados', err);
      }
    };
    fetchMe();
  }, []);

  const token = localStorage.getItem('token');
  let currentUserId = null;
  let nomeBase = 'Jogador';
  if (token) {
    try {
      const payloadBase64 = token.split('.')[1];
      const decodedPayload = JSON.parse(atob(payloadBase64));
      currentUserId = parseInt(decodedPayload.sub);
      nomeBase = decodedPayload.nome || 'Jogador';
    } catch (e) { }
  }

  const nomeExibicao = meusDados?.nome || nomeBase;
  const nenhumEventoAtivo = !evento || evento?.status_evento === 'ENCERRADO' || evento?.status_evento === 'CANCELADO';

  const minhaPresenca = evento?.presencas?.find(p => p.usuario_id === currentUserId);
  const statusPresenca = minhaPresenca?.status_jogo || 'PENDENTE';
  const vaiChurrasco = minhaPresenca?.vai_churrasco || false;
  const minhaPosicao = minhaPresenca?.posicao || 'LINHA';

  const handlePresenca = (status, posicao = minhaPosicao) => {
    atualizarPresenca(status, posicao, vaiChurrasco);
    if (status === 'VOU' && posicao === 'LINHA') {
        setShowPositionSelection(false);
    }
  };

  const handleToggleChurrasco = () => {
    if (statusPresenca === 'PENDENTE' || statusPresenca === 'NAO_VOU') {
      atualizarPresenca('VOU', minhaPosicao, true);
    } else {
      atualizarPresenca('VOU', minhaPosicao, !vaiChurrasco);
    }
  };

  const formatarData = (dataStr, horaStr) => {
    if (!dataStr) return 'Carregando data...';
    try {
      const partes = dataStr.split('-');
      const data = new Date(partes[0], partes[1] - 1, partes[2]);
      const diasSemana = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];
      const diaSem = diasSemana[data.getDay()];
      const dia = partes[2];
      const hora = horaStr ? horaStr.substring(0, 5) : '';
      return `${diaSem}, ${dia} - ${hora}`;
    } catch (e) {
      return dataStr;
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary border-t-transparent"></div>
      </div>
    );
  }

  const presencasConfirmadas = evento?.presencas?.filter(p => p.status_jogo === 'VOU') || [];
  const qtdGoleiros = presencasConfirmadas.filter(p => p.posicao === 'GOL').length;
  const qtdLinha = presencasConfirmadas.filter(p => p.posicao === 'LINHA').length;
  const alertaGoleiro = qtdGoleiros < 2 && evento; // MVP: mínimo 2 goleiros

  return (
    <div className="grid grid-cols-4 md:grid-cols-12 gap-gutter w-full">
      {/* Welcome & Summary Bento Grid */}
      <section className="mb-8 col-span-4 md:col-span-12">
        <h2 className="font-headline-lg-mobile md:font-headline-lg text-headline-lg-mobile md:text-headline-lg mb-4 flex items-center">
          E aí, {nomeExibicao.split(' ')[0]}! 
          <img src="/assets/golden_ball_3d.png" className="w-8 h-8 inline-block ml-2 drop-shadow-sm" alt="bola" />
        </h2>
        <div className="grid grid-cols-3 gap-3 md:gap-4">
          <div className="bento-card bg-surface flex flex-col items-center justify-center gap-2 p-4 text-center">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary mb-1">
              <span className="material-symbols-outlined icon-fill">emoji_events</span>
            </div>
            <span className="font-body-sm text-[11px] text-on-surface-variant uppercase tracking-wider font-bold">Pontos</span>
            <span className="font-display-lg text-title-lg text-on-surface font-extrabold">{meusDados?.pontos_ranking || 0}</span>
          </div>
          <div className="bento-card bg-surface flex flex-col items-center justify-center gap-2 p-4 text-center">
            <div className="w-10 h-10 rounded-full bg-secondary-container/30 flex items-center justify-center text-secondary-container mb-1">
              <span className="material-symbols-outlined icon-fill">star</span>
            </div>
            <span className="font-body-sm text-[11px] text-on-surface-variant uppercase tracking-wider font-bold">Galera</span>
            <span className="font-display-lg text-title-lg text-on-surface font-extrabold">{meusDados?.nota_galera_media ? meusDados.nota_galera_media.toFixed(1) : '-'}</span>
          </div>
          <div className="bento-card bg-surface flex flex-col items-center justify-center gap-2 p-4 text-center">
            <div className="w-10 h-10 rounded-full bg-tertiary/10 flex items-center justify-center text-tertiary mb-1">
              <span className="material-symbols-outlined icon-fill">shield</span>
            </div>
            <span className="font-body-sm text-[11px] text-on-surface-variant uppercase tracking-wider font-bold">Admin</span>
            <span className="font-display-lg text-title-lg text-on-surface font-extrabold">{meusDados?.nota_admin ? meusDados.nota_admin.toFixed(1) : '-'}</span>
          </div>
        </div>
      </section>

      {error && (
        <div className="col-span-4 p-3 bg-error-container text-on-error-container text-body-sm rounded-standard mb-6">
          {error}
        </div>
      )}

      {/* Next Match Card */}
      <section className="col-span-4 md:col-span-8 mb-6">
        <div className="bento-card p-6 relative overflow-hidden bg-surface border border-outline/10">
          {!nenhumEventoAtivo && (
            <div className="absolute top-0 right-0 bg-primary/10 text-primary px-4 py-1.5 rounded-bl-3xl font-label-bold text-label-bold flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse shadow-[0_0_8px_rgba(52,199,89,0.8)]"></span>
              {evento.status_evento === 'AGENDADO' ? 'Agendado' :
               evento.status_evento === 'PRESENCA_ABERTA' ? 'Lista Aberta' :
               evento.status_evento === 'VOTACAO_ABERTA' ? 'Votação Aberta' :
               evento.status_evento === 'ENCERRADO' ? 'Encerrado' :
               evento.status_evento === 'CANCELADO' ? 'Cancelado' : 
               evento.status_evento}
            </div>
          )}
          <h3 className="font-headline-md text-title-lg font-bold mb-4 mt-2">Próxima Pelada</h3>
          
          {!nenhumEventoAtivo ? (
            <>
              <div className="flex flex-col gap-3 mb-6">
                <div className="flex items-center gap-3 text-on-surface-variant">
                  <span className="material-symbols-outlined text-[20px] text-primary">calendar_today</span>
                  <span className="font-body-lg font-semibold">{formatarData(evento.data_jogo, evento.hora_inicio)}</span>
                </div>
                <div className="flex items-center justify-between gap-3 text-on-surface-variant">
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-[20px] text-primary">stadium</span>
                    <div className="flex flex-col">
                      <span className="font-body-lg font-semibold text-on-surface">Arena Oficial</span>
                      {evento.endereco && (
                        <span className="font-body-sm text-[12px] truncate max-w-[150px] md:max-w-[200px]" title={evento.endereco}>
                          {evento.endereco}
                        </span>
                      )}
                    </div>
                  </div>
                  {evento.endereco && (
                    <a 
                      href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(evento.endereco)}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-primary font-label-bold text-[13px] bg-primary/10 px-4 py-2.5 rounded-xl hover:bg-primary/20 transition-colors"
                    >
                      <span className="material-symbols-outlined text-[16px]">location_on</span>
                      GPS
                    </a>
                  )}
                </div>
              </div>

              {evento.status_evento === 'PRESENCA_ABERTA' && (
                <div className="flex flex-col gap-3">
                  <div className="flex gap-3">
                    <button 
                      onClick={() => {
                        if (statusPresenca === 'VOU') {
                          setShowPositionSelection(!showPositionSelection);
                        } else {
                          handlePresenca('VOU');
                          setShowPositionSelection(true);
                        }
                      }}
                      disabled={actionLoading}
                      className={`flex-1 font-label-bold text-[13px] py-3 rounded-2xl transition-all flex items-center justify-center gap-2 shadow-sm ${
                        statusPresenca === 'VOU' 
                        ? 'bg-primary text-on-primary font-bold shadow-bento' 
                        : 'bg-surface-variant/50 text-on-surface-variant hover:bg-surface-variant'
                      }`}
                    >
                      <span className="material-symbols-outlined text-[18px]">check_circle</span>
                      Vou
                    </button>

                    <button 
                      onClick={() => {
                        handlePresenca('PENDENTE');
                        setShowPositionSelection(false);
                      }}
                      disabled={actionLoading}
                      className={`flex-1 font-label-bold text-[13px] py-3 rounded-2xl transition-all flex items-center justify-center gap-2 shadow-sm ${
                        statusPresenca === 'PENDENTE'
                        ? 'bg-[#FF9500] text-white font-bold shadow-bento'
                        : 'bg-surface-variant/50 text-on-surface-variant hover:bg-surface-variant'
                      }`}
                    >
                      <span className="material-symbols-outlined text-[18px]">help</span>
                      Pendente
                    </button>

                    <button 
                      onClick={() => {
                        handlePresenca('NAO_VOU');
                        setShowPositionSelection(false);
                      }}
                      disabled={actionLoading}
                      className={`flex-1 font-label-bold text-[13px] py-3 rounded-2xl transition-all flex items-center justify-center gap-2 shadow-sm ${
                        statusPresenca === 'NAO_VOU'
                        ? 'bg-error text-white font-bold shadow-bento'
                        : 'bg-surface-variant/50 text-on-surface-variant hover:bg-surface-variant'
                      }`}
                    >
                      <span className="material-symbols-outlined text-[18px]">cancel</span>
                      Não Vou
                    </button>
                  </div>

                  {/* Seleção de Posição Expansível */}
                  {showPositionSelection && statusPresenca === 'VOU' && (
                    <div className="flex flex-col gap-3 mt-1 bg-surface-variant/20 p-4 rounded-2xl border border-outline/10">
                      <span className="font-label-bold text-[11px] text-on-surface-variant uppercase text-center font-bold tracking-wider">Qual posição?</span>
                      <div className="flex gap-3">
                        <button 
                          onClick={() => handlePresenca('VOU', 'LINHA')}
                          className={`flex-1 font-body-md font-bold py-2.5 rounded-xl transition-colors shadow-sm ${
                            minhaPosicao === 'LINHA' ? 'bg-primary/20 text-primary border border-primary/30' : 'bg-surface text-on-surface-variant border border-outline/10 hover:border-primary/50'
                          }`}
                        >
                          Linha
                        </button>
                        <button 
                          onClick={() => handlePresenca('VOU', 'GOL')}
                          className={`flex-1 font-body-md font-bold py-2.5 rounded-xl transition-colors shadow-sm ${
                            minhaPosicao === 'GOL' ? 'bg-primary/20 text-primary border border-primary/30' : 'bg-surface text-on-surface-variant border border-outline/10 hover:border-primary/50'
                          }`}
                        >
                          Goleiro
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="py-8 text-center text-on-surface-variant">
              Nenhuma pelada agendada.
            </div>
          )}
        </div>
      </section>

      {/* Sidebar / Secondary Content */}
      <div className="col-span-4 md:col-span-4 flex flex-col gap-6">
        
        {/* Barbecue Card */}
        {!nenhumEventoAtivo && evento?.flag_churrasco && (
          <section>
            <div className="bento-card p-6 relative overflow-hidden bg-gradient-to-br from-[#FF9500] to-[#FF3B30] text-white">
              <div className="absolute -right-6 -top-6 opacity-30 pointer-events-none">
                <img src="/assets/barbecue_3d.png" alt="Churrasco" className="w-40 h-40 object-contain drop-shadow-lg filter blur-[2px]" />
              </div>
              <div className="relative z-10 flex flex-col h-full">
                <div className="flex items-center gap-3 mb-2">
                  <img src="/assets/barbecue_3d.png" alt="Churrasco" className="w-10 h-10 object-contain drop-shadow-md" />
                  <h3 className="font-headline-md text-title-lg font-bold drop-shadow-sm">Churrasco</h3>
                </div>
                <p className="font-display-lg text-[40px] font-extrabold mb-5 tracking-tight drop-shadow-sm">
                  R$ {Math.floor(evento.valor_churrasco)}<span className="text-[20px]">,{(evento.valor_churrasco % 1).toFixed(2).substring(2)}</span>
                </p>
                <div className="flex gap-3">
                  <button 
                    onClick={handleToggleChurrasco}
                    disabled={actionLoading}
                    className={`flex-1 font-label-bold text-label-bold py-3 rounded-2xl transition-all shadow-sm ${
                      vaiChurrasco ? 'bg-white text-[#FF3B30] font-bold' : 'bg-white/20 text-white hover:bg-white/30 backdrop-blur-sm'
                    }`}
                  >
                    {vaiChurrasco ? 'Tô dentro ✅' : 'Participar'}
                  </button>
                  {vaiChurrasco && (
                     <button 
                       onClick={handleToggleChurrasco}
                       disabled={actionLoading}
                       className="px-5 bg-black/20 text-white font-label-bold text-label-bold py-3 rounded-2xl hover:bg-black/30 backdrop-blur-sm transition-all"
                     >
                       Sair
                     </button>
                  )}
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Current List Overview */}
        {!nenhumEventoAtivo && (
          <section className="bg-surface-container-lowest border border-outline-variant/30 rounded-xl p-4 shadow-ambient-1">
            <div className="flex justify-between items-center mb-3 border-b border-outline-variant/20 pb-2">
              <h3 className="font-headline-md text-headline-md">Lista Atual</h3>
              <span className="font-label-bold text-label-bold text-primary">{presencasConfirmadas.length} total</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-outline-variant/10">
              <span className="font-body-md text-body-md text-on-surface-variant">Linha</span>
              <span className="font-headline-md text-headline-md">{qtdLinha}</span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="font-body-md text-body-md text-on-surface-variant">Goleiros</span>
              <span className={`font-headline-md text-headline-md ${alertaGoleiro ? 'text-error font-bold' : ''}`}>{qtdGoleiros}</span>
            </div>

            {/* Goalkeeper Alert */}
            {alertaGoleiro && (
              <div className="mt-3 bg-error-container text-on-error-container p-3 rounded-lg flex items-start gap-2 border border-error/20">
                <span className="material-symbols-outlined text-[20px] shrink-0 mt-0.5">warning</span>
                <p className="font-body-sm text-body-sm">
                  <strong className="font-label-bold text-label-bold block mb-0.5">Alerta: Precisamos de goleiro!</strong>
                  Risco de revezamento no gol.
                </p>
              </div>
            )}
          </section>
        )}
      </div>

      {/* Lista Completa de Confirmados */}
      {!nenhumEventoAtivo && presencasConfirmadas.length > 0 && (
        <section className="col-span-4 md:col-span-12 mt-2 mb-8">
          <div className="bento-card p-6 border border-outline/10 bg-surface">
            <div className="flex items-center gap-3 mb-5 pb-4 border-b border-outline/10">
              <span className="material-symbols-outlined text-primary text-[28px] icon-fill">group</span>
              <h3 className="font-headline-md text-title-lg text-on-surface font-bold">Quem já confirmou <span className="text-primary">({presencasConfirmadas.length})</span></h3>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {presencasConfirmadas.map(jogador => (
                <div key={jogador.usuario_id} className="bento-card bg-surface-variant/30 p-3 flex items-center justify-between border border-outline/10 hover:border-primary/30 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-surface shadow-sm flex items-center justify-center text-on-surface-variant font-bold shrink-0 overflow-hidden border-2 border-surface">
                      {jogador.usuario_foto_url ? (
                        <img src={getFotoUrl(jogador.usuario_foto_url)} alt={jogador.usuario_nome} className="w-full h-full object-cover" />
                      ) : (
                        jogador.usuario_nome.charAt(0)
                      )}
                    </div>
                    <div className="flex flex-col">
                      <span className="font-headline-md text-body-lg font-bold text-on-surface truncate max-w-[130px]" title={jogador.usuario_nome}>{jogador.usuario_nome}</span>
                      <span className="font-label-bold text-[11px] text-primary uppercase tracking-wider">{jogador.posicao === 'GOL' ? 'Goleiro' : 'Linha'}</span>
                    </div>
                  </div>
                  {jogador.vai_churrasco && (
                    <div className="w-8 h-8 rounded-full bg-[#FF9500]/20 flex items-center justify-center text-[#FF9500]" title="Confirmado no Churrasco">
                      <span className="material-symbols-outlined text-[18px] icon-fill">local_fire_department</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

    </div>
  );
}
