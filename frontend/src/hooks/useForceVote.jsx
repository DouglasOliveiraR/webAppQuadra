import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

/**
 * Este componente simula o Guard Pattern de Force Vote.
 * Em um app real, ele bateria na API `/api/eventos/atual/status` para descobrir se 
 * o evento está em 'VOTACAO_ABERTA' e se o usuário atual tem pendências de voto.
 * 
 * Por enquanto, estamos usando um mock simples no localStorage para simular o comportamento.
 */
export function ForceVoteGuard({ children }) {
  const location = useLocation();
  const forceVoteAtivo = localStorage.getItem('mock_force_vote') === 'true';

  if (forceVoteAtivo && location.pathname !== '/votos') {
    // Redireciona o usuário sempre para a página de votos
    return <Navigate to="/votos" replace />;
  }

  return children;
}
