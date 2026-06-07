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
      <section className="col-span-4 md:col-span-12 mb-6">
        <h2 className="font-headline-lg-mobile md:font-headline-lg text-headline-lg-mobile md:text-headline-lg mb-4">E aí, {nomeExibicao.split(' ')[0]}! ⚽</h2>
        <div className="grid grid-cols-3 gap-2 md:gap-4">
          <div className="bg-surface-container-lowest border border-outline-variant/30 rounded-lg p-3 shadow-ambient-1 hover:shadow-ambient-2 transition-all duration-200 flex flex-col items-center justify-center gap-1">
            <span className="material-symbols-outlined text-primary icon-fill text-[24px]">emoji_events</span>
            <span className="font-body-sm text-body-sm text-on-surface-variant">Pontos</span>
            <span className="font-headline-md text-headline-md text-on-surface font-bold">{meusDados?.pontos_ranking || 0}</span>
          </div>
          <div className="bg-surface-container-lowest border border-outline-variant/30 rounded-lg p-3 shadow-ambient-1 hover:shadow-ambient-2 transition-all duration-200 flex flex-col items-center justify-center gap-1">
            <span className="material-symbols-outlined text-secondary-container icon-fill text-[24px]">star</span>
            <span className="font-body-sm text-body-sm text-on-surface-variant">Galera</span>
            <span className="font-headline-md text-headline-md text-on-surface font-bold">{meusDados?.nota_galera_media ? meusDados.nota_galera_media.toFixed(1) : '-'}</span>
          </div>
          <div className="bg-surface-container-lowest border border-outline-variant/30 rounded-lg p-3 shadow-ambient-1 hover:shadow-ambient-2 transition-all duration-200 flex flex-col items-center justify-center gap-1">
            <span className="material-symbols-outlined text-tertiary icon-fill text-[24px]">shield</span>
            <span className="font-body-sm text-body-sm text-on-surface-variant">Admin</span>
            <span className="font-headline-md text-headline-md text-on-surface font-bold">{meusDados?.nota_admin ? meusDados.nota_admin.toFixed(1) : '-'}</span>
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
        <div className="bg-surface-container-lowest border border-outline-variant/30 rounded-xl p-4 md:p-6 shadow-ambient-1 relative overflow-hidden">
          {!nenhumEventoAtivo && (
            <div className="absolute top-0 right-0 bg-primary-container text-on-primary-container px-3 py-1 rounded-bl-xl font-label-bold text-label-bold flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
              {evento.status_evento === 'AGENDADO' ? 'Agendado' :
               evento.status_evento === 'PRESENCA_ABERTA' ? 'Lista Aberta' :
               evento.status_evento === 'VOTACAO_ABERTA' ? 'Votação Aberta' :
               evento.status_evento === 'ENCERRADO' ? 'Encerrado' :
               evento.status_evento === 'CANCELADO' ? 'Cancelado' : 
               evento.status_evento}
            </div>
          )}
          <h3 className="font-headline-md text-headline-md mb-2 mt-4 md:mt-0">Próxima Pelada</h3>
          
          {!nenhumEventoAtivo ? (
            <>
              <div className="flex flex-col gap-2 mb-6">
                <div className="flex items-center gap-2 text-on-surface-variant">
                  <span className="material-symbols-outlined text-[20px]">calendar_today</span>
                  <span className="font-body-md text-body-md">{formatarData(evento.data_jogo, evento.hora_inicio)}</span>
                </div>
                <div className="flex items-center justify-between gap-2 text-on-surface-variant">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-[20px]">stadium</span>
                    <div className="flex flex-col">
                      <span className="font-body-md text-body-md text-on-surface">Arena Oficial</span>
                      {evento.endereco && (
                        <span className="font-body-sm text-body-sm truncate max-w-[150px] md:max-w-full text-tertiary" title={evento.endereco}>
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
                      className="flex items-center gap-1 text-primary hover:text-primary/80 font-label-bold text-[12px] bg-primary/10 px-3 py-2 rounded-lg transition-colors"
                    >
                      <span className="material-symbols-outlined text-[16px]">location_on</span>
                      GPS
                    </a>
                  )}
                </div>
              </div>

              {evento.status_evento === 'PRESENCA_ABERTA' && (
                <div className="flex flex-col gap-3">
                  <div className="flex gap-2">
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
                      className={`flex-1 font-label-bold text-label-bold py-2 rounded-lg transition-all flex flex-col items-center justify-center gap-1 ${
                        statusPresenca === 'VOU' 
                        ? 'bg-primary text-on-primary shadow-md' 
                        : 'bg-surface-variant text-on-surface-variant hover:bg-surface-variant/80'
                      }`}
                    >
                      <span className="material-symbols-outlined text-[20px]">check_circle</span>
                      Vou
                    </button>

                    <button 
                      onClick={() => {
                        handlePresenca('PENDENTE');
                        setShowPositionSelection(false);
                      }}
                      disabled={actionLoading}
                      className={`flex-1 font-label-bold text-label-bold py-2 rounded-lg transition-all flex flex-col items-center justify-center gap-1 ${
                        statusPresenca === 'PENDENTE'
                        ? 'bg-tertiary text-on-tertiary shadow-md'
                        : 'bg-surface-variant text-on-surface-variant hover:bg-surface-variant/80'
                      }`}
                    >
                      <span className="material-symbols-outlined text-[20px]">help</span>
                      Pendente
                    </button>

                    <button 
                      onClick={() => {
                        handlePresenca('NAO_VOU');
                        setShowPositionSelection(false);
                      }}
                      disabled={actionLoading}
                      className={`flex-1 font-label-bold text-label-bold py-2 rounded-lg transition-all flex flex-col items-center justify-center gap-1 ${
                        statusPresenca === 'NAO_VOU'
                        ? 'bg-error text-on-error shadow-md'
                        : 'bg-surface-variant text-on-surface-variant hover:bg-surface-variant/80'
                      }`}
                    >
                      <span className="material-symbols-outlined text-[20px]">cancel</span>
                      Não Vou
                    </button>
                  </div>

                  {/* Seleção de Posição Expansível */}
                  {showPositionSelection && statusPresenca === 'VOU' && (
                    <div className="flex flex-col gap-2 mt-2 bg-surface-container-low p-3 rounded-lg border border-outline-variant/30">
                      <span className="font-label-bold text-label-bold text-on-surface-variant uppercase text-center mb-1">Qual posição?</span>
                      <div className="flex gap-2">
                        <button 
                          onClick={() => handlePresenca('VOU', 'LINHA')}
                          className={`flex-1 font-body-md text-body-md py-2 rounded-md transition-colors ${
                            minhaPosicao === 'LINHA' ? 'bg-primary-container text-on-primary-container border-primary' : 'bg-surface-container-lowest text-on-surface border border-outline-variant hover:border-primary hover:text-primary'
                          }`}
                        >
                          Linha
                        </button>
                        <button 
                          onClick={() => handlePresenca('VOU', 'GOL')}
                          className={`flex-1 font-body-md text-body-md py-2 rounded-md transition-colors ${
                            minhaPosicao === 'GOL' ? 'bg-primary-container text-on-primary-container border-primary' : 'bg-surface-container-lowest text-on-surface border border-outline-variant hover:border-primary hover:text-primary'
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
            <div className="py-6 text-center text-on-surface-variant">
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
            <div className="rounded-xl p-4 md:p-6 shadow-ambient-1 relative overflow-hidden bg-gradient-to-br from-secondary-container to-barbecue-fire text-on-primary" style={{boxShadow: "inset 0 0 0 1px rgba(255,255,255,0.2)"}}>
              <div className="flex items-center gap-2 mb-2">
                <span className="material-symbols-outlined icon-fill">local_fire_department</span>
                <h3 className="font-headline-md text-headline-md" style={{textShadow: "0 1px 2px rgba(0,0,0,0.2)"}}>Churrasco Pós-Jogo</h3>
              </div>
              <p className="font-display-lg text-display-lg font-bold mb-4" style={{textShadow: "0 2px 4px rgba(0,0,0,0.2)"}}>
                R$ {Math.floor(evento.valor_churrasco)}<span className="text-[24px]">,{(evento.valor_churrasco % 1).toFixed(2).substring(2)}</span>
              </p>
              <div className="flex gap-2">
                <button 
                  onClick={handleToggleChurrasco}
                  disabled={actionLoading}
                  className={`flex-1 font-label-bold text-label-bold py-2 rounded-lg transition-all shadow-sm ${
                    vaiChurrasco ? 'bg-white text-secondary' : 'bg-transparent border border-white text-white hover:bg-white/10'
                  }`}
                >
                  {vaiChurrasco ? 'Tô dentro ✅' : 'Participar'}
                </button>
                {vaiChurrasco && (
                   <button 
                     onClick={handleToggleChurrasco}
                     disabled={actionLoading}
                     className="flex-1 bg-transparent border border-white text-white font-label-bold text-label-bold py-2 rounded-lg hover:bg-white/10 transition-all"
                   >
                     Passo
                   </button>
                )}
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
          <div className="bg-surface-container-lowest border border-outline-variant/30 rounded-xl p-4 md:p-6 shadow-ambient-1">
            <div className="flex items-center gap-2 mb-4 border-b border-outline-variant/20 pb-3">
              <span className="material-symbols-outlined text-primary text-[24px]">group</span>
              <h3 className="font-headline-md text-headline-md text-on-surface">Quem já confirmou ({presencasConfirmadas.length})</h3>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {presencasConfirmadas.map(jogador => (
                <div key={jogador.usuario_id} className="flex items-center justify-between p-3 rounded-lg bg-surface-container-low hover:bg-surface-container transition-colors border border-outline-variant/20">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-surface-variant flex items-center justify-center text-on-surface-variant font-bold shrink-0 overflow-hidden shadow-sm">
                      {jogador.usuario_foto_url ? (
                        <img src={getFotoUrl(jogador.usuario_foto_url)} alt={jogador.usuario_nome} className="w-full h-full object-cover" />
                      ) : (
                        jogador.usuario_nome.charAt(0)
                      )}
                    </div>
                    <div className="flex flex-col">
                      <span className="font-label-lg text-label-lg font-bold text-on-surface truncate max-w-[120px]" title={jogador.usuario_nome}>{jogador.usuario_nome}</span>
                      <span className="font-body-sm text-body-sm text-tertiary">{jogador.posicao === 'GOL' ? 'Goleiro' : 'Linha'}</span>
                    </div>
                  </div>
                  {jogador.vai_churrasco && (
                    <div className="bg-secondary-container/20 text-secondary-container px-2 py-1 rounded-full flex items-center justify-center" title="Confirmado no Churrasco">
                      <span className="material-symbols-outlined text-[16px]">local_fire_department</span>
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
