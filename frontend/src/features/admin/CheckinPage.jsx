import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import api from '../../services/api';

const MOCK_PLAYERS = [
  { id: 2, nome: 'João Artilheiro', posicao: 'LINHA', chegou: null },
  { id: 3, nome: 'Carlos Paredão', posicao: 'GOL', chegou: null },
];

export function CheckinPage() {
  const [jogadores, setJogadores] = useState(MOCK_PLAYERS);
  const [loading, setLoading] = useState(null);
  const [error, setError] = useState('');

  const handleCheckin = async (usuarioId, chegou, falta_justificada = false) => {
    setLoading(usuarioId);
    setError('');
    try {
      await api.post(`/eventos/1/checkin/${usuarioId}`, { chegou, falta_justificada });
      setJogadores(prev => prev.map(j => 
        j.id === usuarioId ? { ...j, chegou, falta_justificada } : j
      ));
    } catch (err) {
      if (err.response?.status === 403) {
        setError('Acesso negado: Apenas Administradores podem realizar o Check-in.');
      } else {
        setError('Erro ao salvar checkin.');
      }
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="flex flex-col gap-6 p-4 pt-8 pb-32">
      <header>
        <h2 className="text-headline-md text-tertiary">Painel do Admin</h2>
        <h1 className="text-headline-lg-mobile text-on-background">Check-in na Quadra</h1>
      </header>

      {error && (
        <div className="p-3 bg-error-container text-on-error-container text-body-sm rounded-standard border border-error/20">
          {error}
        </div>
      )}

      <div className="space-y-4">
        {jogadores.map(jogador => (
          <Card key={jogador.id} className="p-4 flex flex-col gap-3">
            <div className="flex justify-between items-center border-b border-surface-variant pb-2">
              <span className="font-bold text-on-background">{jogador.nome}</span>
              <span className="text-xs font-bold px-2 py-1 bg-surface-variant text-tertiary rounded-pill">{jogador.posicao}</span>
            </div>
            
            <div className="flex gap-2">
              <Button 
                variant={jogador.chegou === true ? 'primary' : 'secondary'}
                className="py-2 text-sm flex-1"
                onClick={() => handleCheckin(jogador.id, true, false)}
                disabled={loading === jogador.id}
              >
                Chegou
              </Button>
              <Button 
                variant={jogador.chegou === false && !jogador.falta_justificada ? 'primary' : 'ghost'}
                className={`py-2 text-sm flex-1 ${jogador.chegou === false && !jogador.falta_justificada ? 'bg-error text-white border-none shadow-lvl1' : 'text-error'}`}
                onClick={() => handleCheckin(jogador.id, false, false)}
                disabled={loading === jogador.id}
              >
                Faltou
              </Button>
              <Button 
                variant={jogador.chegou === false && jogador.falta_justificada ? 'primary' : 'ghost'}
                className={`py-2 text-sm flex-1 ${jogador.chegou === false && jogador.falta_justificada ? 'bg-secondary text-white border-none shadow-lvl1' : 'text-secondary'}`}
                onClick={() => handleCheckin(jogador.id, false, true)}
                disabled={loading === jogador.id}
              >
                Avisou
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
