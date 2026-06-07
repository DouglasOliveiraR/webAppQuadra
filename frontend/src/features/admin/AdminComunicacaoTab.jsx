import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { showToast } from '../../components/ui/Toast';

export function AdminComunicacaoTab({ eventoId, evento }) {
  const [loading, setLoading] = useState(false);
  
  // Função auxiliar para abrir o WhatsApp
  const sendToWhatsApp = (text) => {
    const encodedText = encodeURIComponent(text);
    // Tenta usar API de Share nativa do celular, senão cai pro WhatsApp
    if (navigator.share && /mobile|android|iphone/i.test(navigator.userAgent)) {
      navigator.share({
        title: 'FUT Pelada FC',
        text: text
      }).catch(console.error);
    } else {
      window.open(`https://wa.me/?text=${encodedText}`, '_blank');
    }
  };

  const handleShareResultados = async () => {
    setLoading(true);
    try {
      const [resRanking, resUltimo] = await Promise.all([
        api.get('/ranking'),
        api.get('/ranking/ultimo-resultado').catch(() => ({ data: null }))
      ]);

      const rankingData = resRanking.data;
      const ultimoData = resUltimo.data;

      // Ordenar por Média Geral
      const rankingSorted = [...rankingData].sort((a, b) => (b.nota_galera_media || 0) - (a.nota_galera_media || 0));

      let text = `\u{1F3C6} *Resultados da Pelada* \u{1F3C6}\n\n`;
      text += `*\u{1F31F} Top 5 - Média Geral*\n`;
      
      const medalhas = ['\u{1F947} 1º', '\u{1F948} 2º', '\u{1F949} 3º', '\u{1F3C5} 4º', '\u{1F3C5} 5º'];
      rankingSorted.slice(0, 5).forEach((jogador, index) => {
        text += `${medalhas[index]} ${jogador.nome} (${(jogador.nota_galera_media || 0).toFixed(1)})\n`;
      });

      if (ultimoData && ultimoData.top5_medias && ultimoData.top5_medias.length > 0) {
        text += `\n*\u{1F525} Top 5 - Último Jogo (Média)*\n`;
        ultimoData.top5_medias.slice(0, 5).forEach((jogador, index) => {
          text += `${medalhas[index]} ${jogador.nome} (${jogador.media.toFixed(1)})\n`;
        });
      }

      if (ultimoData && ultimoData.vencedores) {
        text += `\n*\u{1F3AD} Destaques do Jogo*\n`;
        const v = ultimoData.vencedores;
        if (v.BOLA_CHEIA?.length) text += `\u{26BD} *Bola Cheia:* ${v.BOLA_CHEIA.map(x=>x.nome).join(', ')} (${v.BOLA_CHEIA[0].votos} votos)\n`;
        if (v.GOL_BONITO?.length) text += `\u{2604}\u{FE0F} *Gol Bonito:* ${v.GOL_BONITO.map(x=>x.nome).join(', ')} (${v.GOL_BONITO[0].votos} votos)\n`;
        if (v.BOLA_MURCHA?.length) text += `\u{1F422} *Bola Murcha:* ${v.BOLA_MURCHA.map(x=>x.nome).join(', ')} (${v.BOLA_MURCHA[0].votos} votos)\n`;
        if (v.LAFON?.length) text += `\u{1F9E4} *Lafon:* ${v.LAFON.map(x=>x.nome).join(', ')} (${v.LAFON[0].votos} votos)\n`;
      }

      text += `\nConfira a lista completa no App!\n\u{1F449} https://futpeladafc.com`;
      
      sendToWhatsApp(text);
    } catch (err) {
      console.error(err);
      showToast('Erro ao gerar resultados', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSharePresenca = async () => {
    setLoading(true);
    try {
      const resUsuarios = await api.get('/usuarios');
      const usuarios = resUsuarios.data;
      const presencas = evento?.presencas || [];

      // Mapear quem confirmou
      const confirmados = [];
      const goleiros = [];
      const ausentes = [];

      usuarios.forEach(u => {
        const p = presencas.find(pres => pres.usuario_id === u.id);
        if (p) {
          const nome = u.nome;
          if (p.status_jogo === 'VOU') {
            if (p.posicao === 'GOL') goleiros.push(nome);
            else confirmados.push(nome);
          } else if (p.status_jogo === 'NAO_VOU') {
            ausentes.push(nome);
          }
        }
      });

      const dateObj = new Date(evento.data_jogo + 'T12:00:00');
      const diaSemana = dateObj.toLocaleDateString('pt-BR', { weekday: 'long' });
      const dataStr = dateObj.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });

      let text = `Lista para ${diaSemana.charAt(0).toUpperCase() + diaSemana.slice(1)} ${dataStr}\n\n`;
      text += `Confirmar no site também:\nhttps://futpeladafc.com\n\n`;

      text += `*Confirmados*\n`;
      confirmados.forEach((n, i) => text += `${i+1} - ${n}\n`);
      if (confirmados.length === 0) text += `(Nenhum confirmado)\n`;

      text += `\n*Goleiros*\n`;
      goleiros.forEach((n, i) => text += `${i+1} - ${n} \u{1F9E4}\n`);
      if (goleiros.length === 0) text += `(Nenhum goleiro)\n`;

      if (ausentes.length > 0) {
        text += `\n*Ausentes*\n`;
        ausentes.forEach((n, i) => text += `${i+1} - ${n} \u{1F691}\n`);
      }

      sendToWhatsApp(text);
    } catch (err) {
      console.error(err);
      showToast('Erro ao gerar lista', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleShareSorteio = async () => {
    setLoading(true);
    try {
      // Usar a mesma lógica de sorteio ou pegar o sorteio salvo
      // Pelo que vi, não tem sorteio salvo no banco, ele é gerado na hora
      const res = await api.post(`/eventos/${eventoId}/sorteio`, { criterio: "MEDIA_GERAL" });
      const times = res.data.times || [];
      
      let text = `\u{26BD} *Times Sorteados!* \u{26BD}\n\n`;
      times.forEach(t => {
        text += `*${t.nome}*\n`;
        t.jogadores.forEach((j, idx) => {
          text += `${idx+1}. ${j.nome} ${j.posicao === 'GOL' ? '\u{1F9E4}' : ''}\n`;
        });
        text += `\n`;
      });
      text += `Cheguem no horário para não atrasar o primeiro tempo!`;

      sendToWhatsApp(text);
    } catch (err) {
      console.error(err);
      showToast('Gere o sorteio primeiro ou confirme jogadores!', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleShareConvite = () => {
    const text = `\u{1F6A8} *VAGAS ABERTAS!* \u{1F6A8}\n\nTemos vagas sobrando para a pelada desta semana.\nQuem tiver convidado/avulso, avise a diretoria para adicionarmos na lista do sorteio!`;
    sendToWhatsApp(text);
  };

  const handleShareFinanceiro = () => {
    const text = `\u{1F4B0} *Atenção Financeiro!* \u{1F4B0}\n\nFala galera, lembrando que o fechamento financeiro (mensalidade/quadra) está em aberto!\nQuem ainda não acertou, por favor envie o Pix para não atrasarmos o pagamento da quadra. Agradecemos a colaboração! \u{1F64F}`;
    sendToWhatsApp(text);
  };

  const buttons = [
    { label: 'Compartilhar Resultados', icon: 'emoji_events', desc: 'Ranking Geral e Destaques', action: handleShareResultados },
    { label: 'Lista de Presença', icon: 'list_alt', desc: 'Confirmados, Goleiros e Ausentes', action: handleSharePresenca },
    { label: 'Sorteio dos Times', icon: 'sports_soccer', desc: 'Times formados do último sorteio', action: handleShareSorteio },
    { label: 'Convite para Avulsos', icon: 'person_add', desc: 'Aviso de vagas sobrando', action: handleShareConvite },
    { label: 'Lembrete Financeiro', icon: 'payments', desc: 'Cobrança genérica sem nomes', action: handleShareFinanceiro }
  ];

  return (
    <div className="space-y-4 fade-in">
      <div className="bg-primary/10 border border-primary/20 rounded-xl p-4 mb-4">
        <h3 className="font-headline-md text-primary text-[16px] mb-2 flex items-center gap-2">
          <span className="material-symbols-outlined">forum</span> Central de Comunicação
        </h3>
        <p className="text-[12px] text-on-surface-variant">
          Gere mensagens prontas e formatadas para compartilhar no WhatsApp da pelada com 1 clique.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {buttons.map((btn, idx) => (
          <button
            key={idx}
            onClick={btn.action}
            disabled={loading}
            className="glass-panel p-4 rounded-xl shadow-ambient-1 hover:bg-surface-container-high transition-colors text-left flex items-start gap-4 active:scale-95"
          >
            <div className="w-10 h-10 rounded-full bg-primary/20 text-primary flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined">{btn.icon}</span>
            </div>
            <div>
              <h4 className="font-bold text-on-surface text-[14px]">{btn.label}</h4>
              <p className="text-[12px] text-on-surface-variant">{btn.desc}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
