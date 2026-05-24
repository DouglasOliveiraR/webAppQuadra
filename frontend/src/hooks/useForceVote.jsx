import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useEvento } from './useEvento';

/**
 * Componente que intercepta a navegação (Guard Pattern) e obriga o jogador a votar
 * caso haja uma votação aberta pós-jogo e ele ainda não tenha votado.
 */
export function ForceVoteGuard({ children }) {
  const location = useLocation();
  const { evento, loading } = useEvento(1);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary border-t-transparent"></div>
      </div>
    );
  }

  let isAdmin = false;
  try {
    const token = localStorage.getItem('token');
    if (token) {
      const payload = JSON.parse(atob(token.split('.')[1]));
      isAdmin = payload.perfil === 'ADMIN';
    }
  } catch (e) {
    console.error('Erro ao ler token no ForceVoteGuard', e);
  }

  // Verifica se o evento está em votação aberta e o usuário logado não votou ainda
  const forceVoteAtivo = !isAdmin && evento?.status_evento === 'VOTACAO_ABERTA' && evento?.usuario_ja_votou === false;

  if (forceVoteAtivo && location.pathname !== '/votos') {
    // Redireciona o usuário para a página de votos
    return <Navigate to="/votos" replace />;
  }

  return children;
}
