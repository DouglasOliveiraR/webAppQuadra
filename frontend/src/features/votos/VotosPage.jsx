import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import api from '../../services/api';

const CATEGORIAS = [
  { id: 'BOLA_CHEIA', titulo: 'Bola Cheia 🌟', desc: 'O craque da partida' },
  { id: 'GOL_BONITO', titulo: 'Gol mais Bonito ⚽', desc: 'Aquele golaço de placa' },
  { id: 'BOLA_MURCHA', titulo: 'Bola Murcha 🥀', desc: 'Aquele que esqueceu o futebol em casa' },
  { id: 'LAFON', titulo: 'Lafon 🪓', desc: 'O lenhador da rodada' },
];

const MOCK_PLAYERS = [
  { id: 2, nome: 'João Artilheiro' },
  { id: 3, nome: 'Carlos Paredão' },
];

export function VotosPage() {
  const [votosFeitos, setVotosFeitos] = useState({});
  const [error, setError] = useState('');

  const handleVotar = async (categoria, candidato_id) => {
    setError('');
    try {
      await api.post(`/eventos/1/votos`, { categoria, candidato_id });
      setVotosFeitos(prev => ({ ...prev, [categoria]: candidato_id }));
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao registrar voto.');
    }
  };

  return (
    <div className="flex flex-col gap-6 p-4 pt-8 pb-32">
      <header className="text-center">
        <h2 className="text-headline-md text-primary font-display font-bold">Votação Pós-Jogo</h2>
        <p className="text-body-sm text-tertiary">Escolha os destaques da partida!</p>
      </header>

      {error && (
        <div className="p-3 bg-error-container text-on-error-container text-body-sm rounded-standard text-center font-medium">
          {error}
        </div>
      )}

      <div className="space-y-6">
        {CATEGORIAS.map(cat => (
          <Card key={cat.id} className="p-4 border-2 border-surface-variant overflow-visible">
            <div className="mb-3">
              <h3 className="font-display font-bold text-lg text-on-background">{cat.titulo}</h3>
              <p className="text-xs text-tertiary">{cat.desc}</p>
            </div>
            
            {votosFeitos[cat.id] ? (
              <div className="p-3 bg-primary/10 text-primary-fixed-variant rounded-standard text-center font-bold">
                Voto Registrado ✅
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                {MOCK_PLAYERS.map(p => (
                  <Button 
                    key={p.id} 
                    variant="ghost" 
                    className="border border-surface-variant justify-start px-4"
                    onClick={() => handleVotar(cat.id, p.id)}
                  >
                    Votar em {p.nome}
                  </Button>
                ))}
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
